import os
import json
from datasets import load_dataset
import numpy as np
import random
from utils import load_field_name
import csv

def preprocess_openai(root='data/openai'):
    instances, categories = [], []
    with open(os.path.join(root, 'samples-1680.jsonl')) as f:
        lines = f.readlines()
    malicious_num = 0
    for line in lines:
        data = json.loads(line)
        instance = data['prompt']
        instances.append(instance)
        category = 0
        for key in data.keys():
            if key != 'prompt' and data[key] != 0:
                category = 1
                malicious_num += 1
                break
        categories.append(category)
    return instances, categories

def preprocess_openai_hate(root='data/openai'):
    instances, categories = [], []
    with open(os.path.join(root, 'samples-1680.jsonl')) as f:
        lines = f.readlines()
    malicious_num = 0
    for line in lines:
        data = json.loads(line)

        if ('H' in list(data.keys()) and data['H']==1) or ('H2' in list(data.keys()) and data['H2']==1):
            instance = data['prompt']
            instances.append(instance)
            categories.append(1)

        flag_mal=0
        for key in data.keys():
            if key != 'prompt' and data[key] != 0:
                flag_mal=1
        if flag_mal==0:
            instance = data['prompt']
            instances.append(instance)
            categories.append(0)
    return instances, categories

def preprocess_openai_sex(root='data/openai'):
    instances, categories = [], []
    with open(os.path.join(root, 'samples-1680.jsonl')) as f:
        lines = f.readlines()
    malicious_num = 0
    for line in lines:
        data = json.loads(line)

        if ('S' in list(data.keys()) and data['S']==1) or ('S3' in list(data.keys()) and data['S3']==1):
            instance = data['prompt']
            instances.append(instance)
            categories.append(1)

        flag_mal = 0
        for key in data.keys():
            if key != 'prompt' and data[key] != 0:
                flag_mal = 1
        if flag_mal == 0:
            instance = data['prompt']
            instances.append(instance)
            categories.append(0)
    return instances, categories

def preprocess_openai_harassment(root='data/openai'):
    instances, categories = [], []
    with open(os.path.join(root, 'samples-1680.jsonl')) as f:
        lines = f.readlines()
    malicious_num = 0
    for line in lines:
        data = json.loads(line)

        if ('HR' in list(data.keys()) and data['HR']==1):
            instance = data['prompt']
            instances.append(instance)
            categories.append(1)

        flag_mal = 0
        for key in data.keys():
            if key != 'prompt' and data[key] != 0:
                flag_mal = 1
        if flag_mal == 0:
            instance = data['prompt']
            instances.append(instance)
            categories.append(0)
    return instances, categories

def preprocess_openai_selfharm(root='data/openai'):
    instances, categories = [], []
    with open(os.path.join(root, 'samples-1680.jsonl')) as f:
        lines = f.readlines()
    malicious_num = 0
    for line in lines:
        data = json.loads(line)

        if ('SH' in list(data.keys()) and data['SH']==1):
            instance = data['prompt']
            instances.append(instance)
            categories.append(1)

        flag_mal = 0
        for key in data.keys():
            if key != 'prompt' and data[key] != 0:
                flag_mal = 1
        if flag_mal == 0:
            instance = data['prompt']
            instances.append(instance)
            categories.append(0)
    return instances, categories

def preprocess_openai_violence(root='data/openai'):
    instances, categories = [], []
    with open(os.path.join(root, 'samples-1680.jsonl')) as f:
        lines = f.readlines()
    malicious_num = 0
    for line in lines:
        data = json.loads(line)

        if ('V' in list(data.keys()) and data['V']==1) or ('V2' in list(data.keys()) and data['V2']==1):
            instance = data['prompt']
            instances.append(instance)
            categories.append(1)

        flag_mal = 0
        for key in data.keys():
            if key != 'prompt' and data[key] != 0:
                flag_mal = 1
        if flag_mal == 0:
            instance = data['prompt']
            instances.append(instance)
            categories.append(0)
    return instances, categories

def preprocess_toxicchat(train=False, size=200):
    dataset = load_dataset("lmsys/toxic-chat", "toxicchat0124")
    if not train:
        dataset = dataset['test']
        instances = dataset['user_input']
        categories = dataset['toxicity']
    else:
        dataset = dataset['train']
        instances = dataset['user_input'][:size]
        categories = dataset['toxicity'][:size]
    return instances, categories

def preprocess_advbench_string(file_path, adv_suffix=None):
    prompts, targets = [], []
    categories = []
    with open(file_path, mode='r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader)
        for row in csv_reader:
            prom = row[0]
            if adv_suffix:
                prom = prom + adv_suffix
            prompts.append(prom)
            categories.append(1)
            if len(row) > 1:
                targets.append(row[1])
    return prompts, categories

def preprocess_hotpot(benign_num):
    instances, categories = [], []
    file = 'hotpot_test_fullwiki_v1.json'
    root = 'data/hotpot'
    with open(os.path.join(root, file)) as f:
        all_data = json.load(f)
    for data in all_data[:benign_num]:
        instance = data['question']
        instances.append(instance)
        categories.append(0)
    return instances, categories

def preprocess_advbench_string_hotpot(root='data/advbench', adv_suffix=None):
    instances, categories = [], []
    with open(os.path.join(root, 'advbench_string_hotpot.jsonl')) as f:
        lines = f.readlines()
    for line in lines:
        data = json.loads(line)
        if data['label']==1 and adv_suffix:
            instances.append(data['input'] + adv_suffix)
        else:
            instances.append(data['input'])
        categories.append(data['label'])
    return instances, categories

def preprocess_advbench_behaviour_hotpot(root='data/advbench', adv_suffix=None):
    instances, categories = [], []
    with open(os.path.join(root, 'advbench_behaviour_hotpot.jsonl')) as f:
        lines = f.readlines()
    for line in lines:
        data = json.loads(line)
        if data['label'] == 1 and adv_suffix:
            instances.append(data['input'] + adv_suffix)
        else:
            instances.append(data['input'])
        categories.append(data['label'])
    return instances, categories

def save_data(data, file_path):
    with open(file_path,'w',encoding='utf-8') as f:
        for line in data:
            f.write(json.dumps(line,ensure_ascii=False)+'\n')
            f.flush()
    return

def fuse_advbench_hotpot(adv_path, output_path, benign_num):
    instance_adv, cat_adv = preprocess_advbench_string(file_path = adv_path)
    instance_hotpot, cat_hotpot = preprocess_hotpot(benign_num)
    instances = instance_adv + instance_hotpot
    categories = cat_adv + cat_hotpot
    output_data = []
    for inst, cate in zip(instances, categories):
        output_data.append({"input": inst, "label": cate})
    save_data(output_data, output_path)

def preprocess_dro(path='./data/DRO'):
    instances, categories = [], []
    path_benign = os.path.join(path, 'dro_benign.txt')
    path_malicious = os.path.join(path, 'dro_malicious.txt')

    with open(path_benign, 'r') as file:
        while True:
            line = file.readline()
            if not line:
                break
            instances.append(line)
            categories.append(0)
    with open(path_malicious, 'r') as file:
        while True:
            line = file.readline()
            if not line:
                break
            instances.append(line)
            categories.append(1)
    return instances, categories

def preprocess_xstest(path='./data/XSTest/xstest_v2_prompts.csv'):
    instances, categories = [], []
    with open(path, mode='r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader, None)
        for row in csv_reader:
            instances.append(row[3])
            categories.append(int('contrast' in row[2]))
    return instances, categories


def preprocess_overkill(path='./data/overkill'):
    instances, categories = [], []
    path_benign = os.path.join(path, 'benign.csv')
    path_malicious = os.path.join(path, 'xstest_v2_prompts.csv')

    with open(path_benign, mode='r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader, None)
        for row in csv_reader:
            instances.append(row[0])
            categories.append(0)
    with open(path_malicious, mode='r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader, None)
        for row in csv_reader:
            if int('contrast' in row[2]):
                instances.append(row[3])
                categories.append(int('contrast' in row[2]))
    return instances, categories


def preprocess_ours(path='./data/ours/ours.csv'):
    instances, categories = [], []
    with open(path, mode='r') as file:
        csv_reader = csv.reader(file)
        next(csv_reader, None)
        for row in csv_reader:
            instances.append(','.join(row[1:]))
            categories.append(int('malicious' in row[0] or 'Malicious' in row[0]))
    return instances, categories

def preprocess_test(root='data/openai'):
    instances, categories = [], []
    with open(os.path.join(root, 'samples-1680.jsonl')) as f:
        lines = f.readlines()
    malicious_num = 0
    for line in lines:
        data = json.loads(line)
        instance = data['prompt']
        instances.append(instance)
        category = 0
        for key in data.keys():
            if key != 'prompt' and data[key] != 0:
                category = 1
                malicious_num += 1
                break
        categories.append(category)
    return instances, categories

def preprocess_beavertail():
    instances, categories = [], []
    round0_dataset = load_dataset('PKU-Alignment/BeaverTails')
    test_data = round0_dataset["30k_test"]
    for x in test_data:
        instances.append(x['prompt']+'\n'+x['response'])
        if x['is_safe']:
            categories.append(0)
        else:
            categories.append(1)
    return instances, categories

def _apply_max_instances(instances, categories, args):
    max_instances = getattr(args, 'max_instances', None)
    if max_instances is None or max_instances <= 0:
        return instances, categories
    subset_strategy = getattr(args, 'subset_strategy', 'head')
    if subset_strategy != 'balanced':
        return instances[:max_instances], categories[:max_instances]

    positive = [idx for idx, category in enumerate(categories) if category == 1]
    negative = [idx for idx, category in enumerate(categories) if category == 0]
    pos_target = min(len(positive), max_instances // 2)
    neg_target = min(len(negative), max_instances - pos_target)
    selected = positive[:pos_target] + negative[:neg_target]
    if len(selected) < max_instances:
        selected_set = set(selected)
        selected.extend(idx for idx in range(len(instances)) if idx not in selected_set)
        selected = selected[:max_instances]
    selected = sorted(selected)
    return [instances[idx] for idx in selected], [categories[idx] for idx in selected]


def load_data(dataset, args):
    if "openai" in dataset:
        instances, categories = preprocess_openai()
    elif dataset == 'toxicchat_train':
        size = getattr(args, 'train_data_size', getattr(args, 'data_size', 200))
        instances, categories = preprocess_toxicchat(train=True, size=size)
    elif dataset == 'toxicchat':
        instances, categories = preprocess_toxicchat()
    elif dataset=='advbench_string':
        instances, categories = preprocess_advbench_string(file_path = './data/advbench/harmful_strings.csv', adv_suffix=args.advbench_suffix)
    elif dataset=='advbench_behaviour':
        instances, categories = preprocess_advbench_string(file_path = './data/advbench/harmful_behaviors.csv', adv_suffix=args.advbench_suffix)
    elif dataset=='advbench_string_hotpot':
        instances, categories = preprocess_advbench_string_hotpot(adv_suffix=args.advbench_suffix)
    elif dataset=='advbench_behaviour_hotpot':
        instances, categories = preprocess_advbench_behaviour_hotpot(adv_suffix=args.advbench_suffix)
    elif dataset=='dro':
        instances, categories = preprocess_dro()
    elif dataset=='xstest':
        instances, categories = preprocess_xstest()
    elif dataset=='overkill':
        instances, categories = preprocess_overkill()
    elif dataset=='ours':
        instances, categories = preprocess_ours()
    elif dataset=='test':
        instances, categories = preprocess_test()
    elif dataset=='beavertail':
        instances, categories = preprocess_beavertail()
    elif dataset=='mod_hate':
        instances, categories = preprocess_openai_hate()
    elif dataset=='mod_sex':
        instances, categories = preprocess_openai_sex()
    elif dataset=='mod_harassment':
        instances, categories = preprocess_openai_harassment()
    elif dataset=='mod_selfharm':
        instances, categories = preprocess_openai_selfharm()
    elif dataset=='mod_violence':
        instances, categories = preprocess_openai_violence()
    else:
        raise ValueError(f"Dataset {dataset} is not supported!")
    return _apply_max_instances(instances, categories, args)

def _implication_pairs_for_model(model_name):
    fields = load_field_name(model_name)
    field_to_idx = {field: idx for idx, field in enumerate(fields)}
    known_pairs = [
        ("harassment/threatening", "harassment"),
        ("violence/graphic", "violence"),
        ("hate/threatening", "hate"),
        ("sexual/minors", "sexual"),
        ("self-harm/intent", "self-harm"),
        ("self-harm/instructions", "self-harm"),
        ("severe_toxicity", "toxicity"),
        ("SEVERE_TOXICITY", "TOXICITY"),
    ]
    return [
        (field_to_idx[child], field_to_idx[parent])
        for child, parent in known_pairs
        if child in field_to_idx and parent in field_to_idx
    ]

def construct_pseudo_training_set(data_size, dim_list, model_names=None):
    scores_all = []
    labels = []
    num_models = len(dim_list)
    implication_pairs = [
        _implication_pairs_for_model(model_name)
        for model_name in model_names
    ] if model_names else [[] for _ in range(num_models)]

    while len(scores_all) < data_size:
        scores_one_instance = []
        violates_implication = False
        for j in range(num_models):
            cur_scores = [np.random.uniform(0, 1) for _ in range(dim_list[j])]
            for child_idx, parent_idx in implication_pairs[j]:
                if cur_scores[child_idx] > 0.5 and cur_scores[parent_idx] < 0.5:
                    violates_implication = True
                    break
            scores_one_instance.append(cur_scores)
            if violates_implication:
                break
        if violates_implication:
            continue
        labels.append(int(max(max(scores) for scores in scores_one_instance) > 0.5))
        scores_all.append(scores_one_instance)
    return scores_all, labels

def sample_real(data_size, model_names, dataset, args):
    scores_all = []
    labels = []
    scores_total = []
    for j in range(len(model_names)):
        score_path =  f'./cache/{model_names[j]}_{dataset}_scores.json'
        with open(score_path, 'r') as file:
            scores = json.load(file)
        scores_total.append(scores)

    instances, categories = load_data(args.dataset, args)
    size_positive_negative = [int(data_size * args.pos_ratio), data_size - int(data_size * args.pos_ratio)]
    for i in range(len(categories)):
        if size_positive_negative[categories[i]]<=0:
            continue
        size_positive_negative[categories[i]] -= 1
        scores_one_instance = []
        for j in range(len(model_names)):
            scores_one_instance.append([scores_total[j][fil][i] for fil in load_field_name(model_names[j])])
        scores_all.append(scores_one_instance)
        labels.append(categories[i])

    return scores_all, labels
