# -*- coding: utf-8 -*-
# @Time    : 2019/4/27 4:05 PM
# @Author  : 公众号：Python疯子
# @File    : 金额转中文.py
# @Software: PyCharm

'''
人民币数字转大写汉字
'''

# coding: utf-8
import warnings
import re
from decimal import Decimal

CN_NUM = {
    '〇': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '零': 0, '壹': 1, '贰': 2,
    '叁': 3, '肆': 4, '伍': 5, '陆': 6, '柒': 7, '捌': 8, '玖': 9, '貮': 2, '两': 2, }

CN_UNIT = {
    '十': 10,
    '拾': 10,
    '百': 100,
    '佰': 100,
    '千': 1000,
    '仟': 1000,
    '万': 10000,
    '萬': 10000,
    '亿': 100000000,
    '億': 100000000,
    '兆': 1000000000000,
    }


def chinese_to_arabic(cn: str) -> int:
    '''中文汉字转阿拉伯数字'''
    unit = 0  # current
    ldig = []  # digest
    for cndig in reversed(cn):
        if cndig in CN_UNIT:
            unit = CN_UNIT.get(cndig)
            if unit == 10000 or unit == 100000000:
                ldig.append(unit)
                unit = 1
        else:
            dig = CN_NUM.get(cndig)
            if unit:
                dig *= unit
                unit = 0
            ldig.append(dig)
    if unit == 10:
        ldig.append(10)
    val, tmp = 0, 0
    for x in reversed(ldig):
        if x == 10000 or x == 100000000:
            val += tmp * x
            tmp = 0
        else:
            tmp += x
    val += tmp
    return val


def cncurrency(value, capital=True, prefix=False, classical=None):
    '''
    标准金钱金额转汉字 带元角分
    参数:
    capital:    True   大写汉字金额
                False  一般汉字金额
    classical:  True   元
                False  圆
    prefix:     True   以'人民币'开头
                False, 无开头
    '''
    if not isinstance(value, (Decimal, str, int)):
        msg = '''
        由于浮点数精度问题，请考虑使用字符串，或者 decimal.Decimal 类。
        因使用浮点数造成误差而带来的可能风险和损失作者概不负责。
        '''
        warnings.warn(msg, UserWarning)
    # 默认大写金额用圆，一般汉字金额用元
    if classical is None:
        classical = True if capital else False

    # 汉字金额前缀
    if prefix is True:
        prefix = '人民币'
    else:
        prefix = ''

    # 汉字金额字符定义
    dunit = ('角', '分')
    if capital:
        num = ('零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖')
        iunit = [None, '拾', '佰', '仟', '万', '拾', '佰', '仟', '亿', '拾', '佰', '仟', '万', '拾', '佰', '仟']
    else:
        num = ('〇', '一', '二', '三', '四', '五', '六', '七', '八', '九')
        iunit = [None, '十', '百', '千', '万', '十', '百', '千', '亿', '十', '百', '千', '万', '十', '百', '千']
    if classical:
        iunit[0] = '元' if classical else '圆'
    # 转换为Decimal，并截断多余小数

    if not isinstance(value, Decimal):
        value = Decimal(value).quantize(Decimal('0.01'))

    # 处理负数
    if value < 0:
        prefix += '负'  # 输出前缀，加负
        value = - value  # 取正数部分，无须过多考虑正负数舍入  # assert - value + value == 0
    # 转化为字符串
    s = str(value)
    if len(s) > 19:
        raise ValueError('金额太大了，不知道该怎么表达。')
    istr, dstr = s.split('.')  # 小数部分和整数部分分别处理
    istr = istr[::-1]  # 翻转整数部分字符串
    so = []  # 用于记录转换结果

    # 零
    if value == 0:
        return prefix + num[0] + iunit[0]
    haszero = False  # 用于标记零的使用
    if dstr == '00':
        haszero = True  # 如果无小数部分，则标记加过零，避免出现“圆零整”

    # 处理小数部分
    # 分
    if dstr[1] != '0':
        so.append(dunit[1])
        so.append(num[int(dstr[1])])
    else:
        so.append('整')  # 无分，则加“整”
    # 角
    if dstr[0] != '0':
        so.append(dunit[0])
        so.append(num[int(dstr[0])])
    elif dstr[1] != '0':
        so.append(num[0])  # 无角有分，添加“零”
        haszero = True  # 标记加过零了

    # 无整数部分
    if istr == '0':
        if haszero:  # 既然无整数部分，那么去掉角位置上的零
            so.pop()
        so.append(prefix)  # 加前缀
        so.reverse()  # 翻转
        return ''.join(so)

    # 处理整数部分
    for i, n in enumerate(istr):
        n = int(n)
        if i % 4 == 0:  # 在圆、万、亿等位上，即使是零，也必须有单位
            if i == 8 and so[-1] == iunit[4]:  # 亿和万之间全部为零的情况
                so.pop()  # 去掉万
            so.append(iunit[i])
            if n == 0:  # 处理这些位上为零的情况
                if not haszero:  # 如果以前没有加过零
                    so.insert(-1, num[0])  # 则在单位后面加零
                    haszero = True  # 标记加过零了
            else:  # 处理不为零的情况
                so.append(num[n])
                haszero = False  # 重新开始标记加零的情况
        else:  # 在其他位置上
            if n != 0:  # 不为零的情况
                so.append(iunit[i])
                so.append(num[n])
                haszero = False  # 重新开始标记加零的情况
            else:  # 处理为零的情况
                if not haszero:  # 如果以前没有加过零
                    so.append(num[0])
                    haszero = True

    # 最终结果
    so.append(prefix)
    so.reverse()
    return ''.join(so)


def cncurrency_money(value, capital=True, prefix=False, classical=None):
    '''
    金额转汉字 不带元角分
    参数:
    capital:    True   大写汉字金额
                False  一般汉字金额
    classical:  True   元
                False  圆
    prefix:     True   以'人民币'开头
                False, 无开头
    '''
    # 默认大写金额用圆，一般汉字金额用元
    if classical is None:
        classical = True if capital else False

    # 汉字金额前缀
    if prefix is True:
        prefix = '人民币'
    else:
        prefix = ''

    # 汉字金额字符定义
    dunit = ('角', '分')
    if capital:
        num = ('零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖')
        iunit = [None, '拾', '佰', '仟', '万', '拾', '佰', '仟', '亿', '拾', '佰', '仟', '万', '拾', '佰', '仟']
    else:
        num = ('〇', '一', '二', '三', '四', '五', '六', '七', '八', '九')
        iunit = [None, '十', '百', '千', '万', '十', '百', '千', '亿', '十', '百', '千', '万', '十', '百', '千']

    # if classical:
    #     iunit[0] = '元' if classical else '圆'
    # 转换为Decimal，并截断多余小数

    if not isinstance(value, Decimal):
        value = Decimal(value).quantize(Decimal('0.01'))

    # 处理负数
    if value < 0:
        prefix += '负'  # 输出前缀，加负
        value = - value  # 取正数部分，无须过多考虑正负数舍入  # assert - value + value == 0
    # 转化为字符串
    s = str(value)
    if len(s) > 19:
        raise ValueError('金额太大了，不知道该怎么表达。')
    istr, dstr = s.split('.')  # 小数部分和整数部分分别处理
    istr = istr[::-1]  # 翻转整数部分字符串
    so = []  # 用于记录转换结果

    # 零
    if value == 0:
        # return prefix + num[0] + iunit[0]
        return prefix + num[0]
    haszero = False  # 用于标记零的使用
    if dstr == '00':
        haszero = True  # 如果无小数部分，则标记加过零，避免出现“圆零整”

    # 处理小数部分
    # 分
    if dstr[1] != '0':
        # so.append(dunit[1])
        so.append(num[int(dstr[1])])
    # else:
    #     so.append('整')  # 无分，则加“整”
    # 角
    if dstr[0] != '0':
        # so.append(dunit[0])
        so.append(num[int(dstr[0])])
        so.append("点")  # 点
    elif dstr[1] != '0':
        so.append(num[0])  # 无角有分，添加“零”
        haszero = True  # 标记加过零了
        so.append("点")  # 点

    # 无整数部分
    if istr == '0':
        # if haszero:  # 既然无整数部分，那么去掉角位置上的零
            # so.pop()
        so.append("零")
        so.append(prefix)  # 加前缀
        so.reverse()  # 翻转
        return ''.join(so)

    # 处理整数部分
    for i, n in enumerate(istr):
        n = int(n)
        if i % 4 == 0:  # 在圆、万、亿等位上，即使是零，也必须有单位
            if i == 8 and so[-1] == iunit[4]:  # 亿和万之间全部为零的情况
                so.pop()  # 去掉万
            so.append(iunit[i])
            if n == 0:  # 处理这些位上为零的情况
                if not haszero:  # 如果以前没有加过零
                    so.insert(-1, num[0])  # 则在单位后面加零
                    haszero = True  # 标记加过零了
            else:  # 处理不为零的情况
                so.append(num[n])
                haszero = False  # 重新开始标记加零的情况
        else:  # 在其他位置上
            if n != 0:  # 不为零的情况
                so.append(iunit[i])
                so.append(num[n])
                haszero = False  # 重新开始标记加零的情况
            else:  # 处理为零的情况
                if not haszero:  # 如果以前没有加过零
                    so.append(num[0])
                    haszero = True

    # 最终结果
    so.append(prefix)

    # 从后往前删
    for temp in so:
        if temp is None:
            so.remove(temp)

    so.reverse()

    chinese_num = ''.join(so)

    # 将 壹拾贰 开头的转为 拾贰
    if chinese_num.startswith("壹拾"):
        chinese_num = re.sub("壹拾", "拾", chinese_num, count=1)

    if "零点" in chinese_num and not chinese_num.startswith("零点"):
        chinese_num = re.sub("零点", "点", chinese_num, count=1)

    return chinese_num

def number_to_chinese(number):
    '''
    身份证ID 数字转汉字
    :param number: 身份证编号
    :return:  身份证编号对应的汉字
    '''
    num2chinese = {"0":"〇",  "1":'一', "2":'二', "3":'三', "4":'四', "5":'五', "6":'六', "7":'七', "8":'八', "9":'九', "X":"X"}

    chinese_num = ""
    for num in number:
        chinese_num += num2chinese.get(num)

    return chinese_num

if __name__ == '__main__':
    # 数字转换
    ret = cncurrency_money(1002.03)
    print(ret)

    # 壹仟零贰点零叁

    # 金额转换 -- 带圆角分
    ret = cncurrency(1002.53)
    print(ret)
    # 壹仟零贰元伍角叁分


    # i = input('请输入金额：')
    # print(cncurrency(i))

    # result = chinese_to_arabic('一百零二亿五千零一万零一千零三十八')
    #
    # print(result)

    ret = number_to_chinese("175X")
    print(ret)

    # 匹配是否包含数字
    # str = '你好2啊789.00是吗'
    # pattern = re.compile('[0-9]+[.0-9]*')
    # match = pattern.findall(str)
    # if match:
    #     print('contains digital')
    #     print(match)
    # else:
    #     print('not contains digital')