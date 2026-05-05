import argparse
from data_loading import load_data
import os
from utils import load_scores_given_path, save_scores, evaluate_auprc, load_field_name, create_batches, evaluate_asr, score_cache_path
from tqdm import tqdm
import openai
import time
from googleapiclient import discovery
from auditnlg.safety.exam import safety_scores
import http.client, urllib.request, urllib.parse, urllib.error, base64
import json
try:
    from llama_recipes.inference.prompt_format_utils import build_prompt, create_conversation, LLAMA_GUARD_CATEGORY
except ImportError:
    from llama_recipes.inference.prompt_format_utils import build_default_prompt, create_conversation, LlamaGuardVersion

    LLAMA_GUARD_CATEGORY = None

    def build_prompt(agent_type, categories, conversation):
        return build_default_prompt(agent_type, conversation, LlamaGuardVersion.LLAMA_GUARD_1)
from enum import Enum
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, AutoModelForSeq2SeqLM

def score_count(scores, fieldnames):
    if not scores:
        return 0
    lengths = [len(scores.get(fil, [])) for fil in fieldnames]
    return min(lengths) if lengths else 0


def save_checkpoint(scores, score_path, args, idx):
    if score_path and not args.not_save and args.checkpoint_every > 0 and (idx + 1) % args.checkpoint_every == 0:
        save_scores(scores, score_path)


def is_rate_limit_error(exc):
    message = str(exc).lower()
    return "rate limit" in message or "too many requests" in message or "429" in message


def with_retries(callable_, args, label):
    last_error = None
    for attempt in range(args.max_retries):
        try:
            return callable_()
        except Exception as exc:
            last_error = exc
            if attempt + 1 >= args.max_retries:
                break
            sleep_seconds = args.retry_sleep * (2 ** attempt)
            if is_rate_limit_error(exc):
                sleep_seconds = max(sleep_seconds, args.rate_limit_sleep)
            print(f"{label} failed on attempt {attempt + 1}/{args.max_retries}: {exc}. Retrying in {sleep_seconds:.1f}s")
            time.sleep(sleep_seconds)
    raise last_error


def run_instances(model, instances, fieldnames, args, initial_scores=None, score_path=None):
    scores = initial_scores or {}
    for fil in fieldnames:
        scores.setdefault(fil, [])
    start_idx = score_count(scores, fieldnames)
    if start_idx:
        print(f"Resuming {model} from cached index {start_idx}/{len(instances)}")

    if model=="openai_mod":
        openai.api_key = args.api_key
        batch_size = max(1, args.api_batch_size)
        with tqdm(total=len(instances), initial=start_idx) as pbar:
            for batch_start in range(start_idx, len(instances), batch_size):
                batch = instances[batch_start:min(batch_start + batch_size, len(instances))]
                moderation_kwargs = {"input": batch}
                if args.openai_moderation_model not in ("", "default", "none", "None"):
                    moderation_kwargs["model"] = args.openai_moderation_model
                response = with_retries(
                    lambda: openai.Moderation.create(**moderation_kwargs),
                    args,
                    f"OpenAI moderation idx={batch_start}:{batch_start + len(batch)}",
                )
                for item in response['results']:
                    category_scores = item['category_scores']
                    for fil in fieldnames:
                        scores[fil].append(category_scores.get(fil, 0.0))
                if score_path and not args.not_save:
                    save_scores(scores, score_path)
                pbar.update(len(batch))
                if args.api_sleep > 0:
                    time.sleep(args.api_sleep)
    elif model=="perspective_api":
        for idx in tqdm(range(start_idx, len(instances)), initial=start_idx, total=len(instances)):
            time.sleep(1)
            try:
                client = discovery.build(
                    "commentanalyzer",
                    "v1alpha1",
                    developerKey=args.api_key,
                    discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
                    static_discovery=False,
                )

                analyze_request = {
                    'comment': {'text': instances[idx]},
                    'requestedAttributes': {'TOXICITY': {}, 'SEVERE_TOXICITY': {}, 'IDENTITY_ATTACK': {}, 'INSULT': {},
                                            'PROFANITY': {}, 'THREAT': {}}
                }
                response = with_retries(
                    lambda: client.comments().analyze(body=analyze_request).execute(),
                    args,
                    f"Perspective idx={idx}",
                )
                response = response["attributeScores"]
                for fil in fieldnames:
                    scores[fil].append(response[fil]['summaryScore']['value'])
            except:
                for fil in fieldnames:
                    scores[fil].append(-1)
            save_checkpoint(scores, score_path, args, idx)
    elif model=="unitaryai_detoxify":
        batches = create_batches(instances[start_idx:], args.batch_size)
        idx = start_idx - 1
        for batch in tqdm(batches):
            example = [{"output": instance} for instance in batch]
            unsafe_scores, unsafe_meta = safety_scores(data=example, method="detoxify", use_cuda=True)
            for i in range(len(unsafe_scores)):
                idx += 1
                for fil in fieldnames:
                    scores[fil].append(unsafe_meta['all_scores'][i][fil])
                save_checkpoint(scores, score_path, args, idx)
    elif model=="azure":
        headers = {
            'Content-Type': 'text/plain',
            'Ocp-Apim-Subscription-Key': args.api_key,
        }
        params = urllib.parse.urlencode({
            'autocorrect': True,
            'PII': False,
            'classify': True,
        })
        conn = http.client.HTTPSConnection('centralus.api.cognitive.microsoft.com')
        cnt = 0
        for i in tqdm(range(start_idx, len(instances)), initial=start_idx, total=len(instances)):
            time.sleep(1)
            query = instances[i].encode('utf-8')
            if len(query)>1024:
                query = query[:1024]
            response = with_retries(
                lambda: (conn.request("POST", "/contentmoderator/moderate/v1.0/ProcessText/Screen?%s" % params, query, headers), conn.getresponse())[1],
                args,
                f"Azure idx={i}",
            )
            data = response.read()
            data = json.loads(data)
            try:
                for fil in fieldnames:
                    scores[fil].append(data["Classification"][fil]["Score"])
            except:
                for fil in fieldnames:
                    scores[fil].append(-1)
                cnt += 1
            save_checkpoint(scores, score_path, args, i)
        print(f'number of exceptions: {cnt}')
        conn.close()
    elif model=="llamaguard":
        class AgentType(Enum):
            AGENT = "Agent"
            USER = "User"
        model_id = "meta-llama/LlamaGuard-7b"
        hf_token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN")
        tokenizer = AutoTokenizer.from_pretrained(model_id, token=hf_token)
        if args.llamaguard_load_in_8bit:
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                token=hf_token,
                device_map="auto",
                load_in_8bit=True,
                low_cpu_mem_usage=True,
            )
        else:
            torch_dtype = torch.float16 if args.llamaguard_float16 else None
            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                token=hf_token,
                torch_dtype=torch_dtype,
                low_cpu_mem_usage=True,
            ).to("cuda")
        model_device = next(model.parameters()).device
        # TODO: add the safe/unsafe logit here

        for i in tqdm(range(start_idx, len(instances)), initial=start_idx, total=len(instances)):
            query = instances[i]
            formatted_prompt = build_prompt(AgentType.USER, LLAMA_GUARD_CATEGORY, create_conversation([query]))
            inputs = tokenizer([formatted_prompt], return_tensors="pt").to(model_device)
            prompt_len = inputs["input_ids"].shape[-1]
            outputs = model.generate(**inputs, max_new_tokens=15, pad_token_id=0, return_dict_in_generate=True, output_scores=True)
            outputs_sequence, outputs_scores = outputs.sequences, outputs.scores
            results = tokenizer.decode(outputs_sequence[0][prompt_len:])
            results = results.strip().split('\n')

            probs_ = torch.softmax(outputs_scores[0][0], dim=-1)
            # print(tokenizer.encode("safe", return_tensors="pt").to("cuda"))
            token_id_safe = int(tokenizer.encode("safe", return_tensors="pt").to(model_device)[0, -1])
            token_id_unsafe = int(tokenizer.encode("unsafe", return_tensors="pt").to(model_device)[0, -1])

            prob_safe = float(probs_[token_id_safe])
            prob_unsafe = float(probs_[token_id_unsafe])
            # prob_unsafe /= (prob_safe + prob_unsafe)
            scores["0"].append(prob_unsafe)

            if len(results) == 1:
                for fil in fieldnames:
                    if fil=="0":
                        continue
                    scores[fil].append(0.)
            else:
                probs_ = torch.softmax(outputs_scores[3][0], dim=-1)
                for fil in fieldnames:
                    if fil=="0":
                        continue
                    token_id = int(tokenizer.encode(fil, return_tensors="pt").to(model_device)[0, 2])
                    prob = float(probs_[token_id])
                    scores[fil].append(prob)
            save_checkpoint(scores, score_path, args, i)
    elif model=="llamaguard2":

        model_id = "meta-llama/Meta-Llama-Guard-2-8B"
        device = "cuda"
        dtype = torch.bfloat16

        tokenizer = AutoTokenizer.from_pretrained(model_id)
        model = AutoModelForCausalLM.from_pretrained(model_id, torch_dtype=dtype, device_map=device)

        for i in tqdm(range(start_idx, len(instances)), initial=start_idx, total=len(instances)):
            chat = [{"role": "user", "content": instances[i]}]

            input_ids = tokenizer.apply_chat_template(chat, return_tensors="pt").to(device)
            prompt_len = input_ids.shape[-1]
            outputs = model.generate(input_ids=input_ids, max_new_tokens=15, pad_token_id=0, return_dict_in_generate=True,output_scores=True)
            outputs_sequence, outputs_scores = outputs.sequences, outputs.scores
            results = tokenizer.decode(outputs_sequence[0][prompt_len:])
            results = results.strip().split('\n')

            probs_ = torch.softmax(outputs_scores[0][0], dim=-1)
            token_id_safe = int(tokenizer.encode("safe", return_tensors="pt").to("cuda")[0, -1])
            token_id_unsafe = int(tokenizer.encode("unsafe", return_tensors="pt").to("cuda")[0, -1])
            prob_safe = float(probs_[token_id_safe])

            prob_unsafe = float(probs_[token_id_unsafe])
            prob_unsafe /= (prob_safe + prob_unsafe)

            scores["0"].append(prob_unsafe)

            if len(results) == 1:
                for fil in fieldnames:
                    if fil == "0":
                        continue
                    scores[fil].append(0.)
            else:
                probs_ = torch.softmax(outputs_scores[3][0], dim=-1)
                for fil in fieldnames:
                    if fil == "0":
                        continue
                    token_id = int(tokenizer.encode(fil, return_tensors="pt").to("cuda")[0, 0])
                    prob = float(probs_[token_id])
                    scores[fil].append(prob)
            save_checkpoint(scores, score_path, args, i)
    elif model=="toxicchat-T5":
        checkpoint = "lmsys/toxicchat-t5-large-v1.0"
        device = "cuda"

        tokenizer = AutoTokenizer.from_pretrained("t5-large")
        model = AutoModelForSeq2SeqLM.from_pretrained(checkpoint).to(device)

        id_negative = tokenizer.encode("negative", return_tensors="pt").to(device)[0][0]
        id_positive = tokenizer.encode("positive", return_tensors="pt").to(device)[0][0]

        prefix = "ToxicChat: "
        for idx in tqdm(range(start_idx, len(instances)), initial=start_idx, total=len(instances)):
            prompt = instances[idx]
            inputs = tokenizer.encode(prefix + prompt, return_tensors="pt").to(device)
            outputs = model.generate(inputs, max_new_tokens=10, return_dict_in_generate=True, output_scores=True)
            logit = outputs[1][0][0]
            probs = torch.nn.functional.softmax(logit, dim=-1)
            prob_safe = probs[id_negative].item()
            prob_unsafe = probs[id_positive].item()
            prob_unsafe = prob_unsafe / (prob_safe + prob_unsafe)
            for fil in fieldnames:
                scores[fil].append(prob_unsafe)
            save_checkpoint(scores, score_path, args, idx)
    else:
        raise ValueError(f"Model {model} is unsupported!")

    return scores

def run_knowledge_model(model ,dataset, args):
    instances, categories = load_data(dataset, args)
    if len(args.advbench_suffix)>0:
        print(f'args.advbench_suffix:')
        print(args.advbench_suffix)
    score_path = score_cache_path(model, dataset, args)
    fieldnames = load_field_name(model)
    if args.print_first_instance:
        print(instances[0])
    st_time = time.time()
    if os.path.exists(score_path) and not args.ignore_cache:
        scores = load_scores_given_path(score_path)
        cached_count = score_count(scores, fieldnames)
        if cached_count >= len(instances):
            print(f"The evaluation for model {model} on dataset {dataset} already exists! Directly loading the results from {score_path}")
        else:
            print(f"Found partial cache for model {model} on dataset {dataset}: {cached_count}/{len(instances)}. Resuming.")
            scores = run_instances(model, instances, fieldnames, args, initial_scores=scores, score_path=score_path)
            if not args.not_save:
                save_scores(scores, score_path)
    else:
        print(f"Running evaluations for model {model} on dataset {dataset}")
        scores = run_instances(model, instances, fieldnames, args, score_path=score_path)
        if not args.not_save:
            save_scores(scores, score_path)

    if dataset=='dro':
        num1 = 0
        num2 = -1
        for fil in fieldnames:
            scores[fil] = scores[fil][num1:num2]
        categories = categories[num1:num2]


    auprc = evaluate_auprc(categories, scores, fieldnames)
    print(f"AUPRC of model {model} on dataset {dataset} is: {auprc}")
    result = {
        "kind": "knowledge_model",
        "model": model,
        "dataset": dataset,
        "advbench_suffix": args.advbench_suffix,
        "num_instances": len(instances),
        "max_instances": args.max_instances,
        "subset_strategy": args.subset_strategy,
        "runtime_seconds": time.time() - st_time,
        "auprc": auprc,
    }
    if model == "openai_mod":
        result["openai_moderation_model"] = args.openai_moderation_model

    if 'adv' in args.dataset:
        racc = evaluate_asr(categories, scores=scores, thresh=0.5, fieldnames=fieldnames, dataset=args.dataset, llamaguard='llama' in model)
        print(f'Robust Accuracy: {racc}')
        result["udr_at_0_5"] = racc

    if 'mod_' in args.dataset:
        acc = evaluate_asr(categories, scores=scores, fieldnames=fieldnames,thresh=0.5,dataset=args.dataset)
        print(f'False negative rate: {1.-acc}')
        result["false_negative_rate_at_0_5"] = 1. - acc

    if args.result_jsonl:
        os.makedirs(os.path.dirname(args.result_jsonl) or ".", exist_ok=True)
        with open(args.result_jsonl, "a", encoding="utf-8") as f:
            f.write(json.dumps(result) + "\n")

    # if 'advbench' in dataset:
    #     acc = evaluate_asr(categories, scores,  fieldnames)
    #     print(f"Robust accuracy of model {model} on dataset {dataset} is: {acc}")


if __name__=='__main__':

    parser = argparse.ArgumentParser(description="Arguments for running knowledge models.")

    parser.add_argument('--knowledge_model_name', type=str, help="name of the knowledge model", choices=['openai_mod', 'perspective_api', 'unitaryai_detoxify', 'azure', 'llamaguard', 'toxicchat-T5', 'llamaguard2'], default='openai_mod')
    parser.add_argument('--dataset', type=str, help="dataset", choices=['openaimod', 'toxicchat', 'toxicchat_train', 'advbench_string', 'advbench_behaviour', 'advbench_behaviour_hotpot', 'advbench_string_hotpot', 'dro', 'xstest', 'overkill', 'ours', 'test', 'beavertail','mod_hate','mod_sex','mod_harassment','mod_selfharm','mod_violence'], default='openaimod')
    parser.add_argument('--api_key', required=False, type=str, default=os.environ.get("OPENAI_API_KEY"), help="api key")
    parser.add_argument('--train_data_size', required=False, type=int, default=200)
    parser.add_argument('--max_instances', required=False, type=int, default=None)
    parser.add_argument('--subset_strategy', choices=['head', 'balanced'], default='head')
    parser.add_argument('--batch_size', required=False, type=int, default=10)
    parser.add_argument('--advbench_suffix', required=False, type=str, default='', help="adversarial suffix for AdvBench")
    parser.add_argument('--not_save', action='store_true')
    parser.add_argument('--ignore_cache', action='store_true', help="Ignore existing score caches and run scoring from scratch.")
    parser.add_argument('--print_first_instance', action='store_true', help="Print the first raw dataset instance for debugging.")
    parser.add_argument('--result_jsonl', type=str, default=None)
    parser.add_argument('--openai_moderation_model', type=str, default=os.environ.get("OPENAI_MODERATION_MODEL", "default"))
    parser.add_argument('--checkpoint_every', type=int, default=25)
    parser.add_argument('--max_retries', type=int, default=5)
    parser.add_argument('--retry_sleep', type=float, default=2.0)
    parser.add_argument('--rate_limit_sleep', type=float, default=float(os.environ.get("RATE_LIMIT_SLEEP", "60")))
    parser.add_argument('--api_sleep', type=float, default=float(os.environ.get("API_SLEEP", "0")))
    parser.add_argument('--api_batch_size', type=int, default=int(os.environ.get("API_BATCH_SIZE", "1")))
    parser.add_argument('--llamaguard_load_in_8bit', action='store_true', help="Load LlamaGuard in 8-bit for constrained local GPUs; not the original released-code path.")
    parser.add_argument('--llamaguard_float16', action='store_true', help="Load LlamaGuard in float16 instead of default precision.")
    args = parser.parse_args()

    run_knowledge_model(args.knowledge_model_name, args.dataset, args)
