# !/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author: Yu Huang
# @Email: yuhuang-cst@foxmail.com

import os

# 限制多进程
# os.environ["MKL_NUM_THREADS"] = "1"
# os.environ["NUMEXPR_NUM_THREADS"] = "1"
# os.environ["OMP_NUM_THREADS"] = "1"
# os.environ["KMP_AFFINITY"] = "disabled"

# 禁用GPU
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

from loguru import logger
from sanic import Sanic, response

from server.utils import process_base, print_request, randstr
from server.service_config import ServiceConfig
from server.constant import LOG_PATH
from PhenoTagger_tagging import get_ont_files, get_vocab_and_model_files, dic_ont, get_nn_model
from tagging_text import bioTag

logger.add(os.path.join(LOG_PATH, 'service.log'), retention='10 days')
logger.info('begining-------')

app = Sanic("PhenoTagger")
app.config.update_config(ServiceConfig)

with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'VERSION'),'r') as fin:
    VERSION = fin.read().strip()

param_dict, biotag_dic, nn_model = None, None, None
def init_engine():
    global param_dict, biotag_dic, nn_model
    param_dict = {
        'model_type': 'biobert',  # cnn, bioformer, or biobert
        'onlyLongest': True,  # False: return overlap concepts, True only longgest
        'abbrRecog': True,  # False: don't identify abbr, True: identify abbr
        'ML_Threshold': 0.95,  # the Threshold of deep learning model
    }
    ontfiles = get_ont_files()
    vocabfiles, modelfile = get_vocab_and_model_files(param_dict['model_type'])
    biotag_dic = dic_ont(ontfiles)
    nn_model = get_nn_model(param_dict['model_type'], vocabfiles, modelfile)


def process_tag_res(text, tag_res):
    res_list = []
    for ele in tag_res:
        span = (int(ele[0]), int(ele[1]))
        res_list.append({
            'span': span,
            'mention_text': text[span[0]: span[1]],
            'hpo_code': ele[2],
            'score': float(ele[3]),
        })
    ret_dict = {'result': res_list, 'version': VERSION, 'log_id': randstr(8)}
    return ret_dict


def process_phenotagger_input_single_request_inner(request):
    """
    Args:
        request:
            - request.json: {
                'text': str,
                'threshold': float,
            }
    Returns:
        dict: {
            'result': list: [{
                'span': (int, int),
                'mention_text': str,
                'hpo_code': str,
                'score': float,
                'polarity': str, # 'negative' | 'positive'
            }, ...]
        }
    """
    # print_request(request) # debug
    text = request.json['text']
    threshold = request.json['threshold']
    tag_res = bioTag(
        text, biotag_dic, nn_model,
        onlyLongest=param_dict['onlyLongest'], abbrRecog=param_dict['abbrRecog'], Threshold=threshold) # Threshold=param_dict['ML_Threshold']
    res = process_tag_res(text, tag_res)
    return res


@app.route('/phenotagger-input-single', methods=['POST'])
async def process_phenotagger_input_single_request(request):
    return process_base(request, process_phenotagger_input_single_request_inner)


if __name__ == '__main__':
    init_engine()
    app.run(host="0.0.0.0", port=8086, workers=1, single_process=True)

