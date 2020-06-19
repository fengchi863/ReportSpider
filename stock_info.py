# coding: utf-8
# Author：fengchi863
# WeChat：lucien863
# Date ：2020/6/18 9:20
'''
https://www.akshare.xyz/zh_CN/latest/tutorial.html
使用akshare获取各个本工程需要的数据
'''

import akshare as ak


# ak.index_stock_info() # 获取指数index列表

def get_index_cons_list(index: str):
    index_stock_cons_df = ak.index_stock_cons(index)
    stk_id_list = index_stock_cons_df['品种代码'].tolist()
    return stk_id_list
