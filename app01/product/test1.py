import itertools

if __name__ == '__main__':
    allparams = [[1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3], [1, 2, 3], ]
    # 1、笛卡尔积 对参数分组全排列
    num = 0
    for i in eval('itertools.product' + str(tuple(allparams))):
        num += 1
        if num < 50000: continue
        print("第 {} 个结果".format(num), i)
