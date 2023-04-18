import akshare as ak
import sys
import requests
import datetime
import tushare as ts
import time

# 获取交易日历
tool_trade_date_hist_sina_df = ak.tool_trade_date_hist_sina()
array = tool_trade_date_hist_sina_df.values

datelist = []
for datee in array:
    strtime = datetime.datetime.strftime(datee[0], "%Y-%m-%d")
    datelist.append(strtime)

Note = open('stack.txt', mode='w',encoding='utf-8')



def stock_is_trade_date(query_date):
    """
    是否为 交易日
    :param query_date: 日期，如 2020-10-01
    :return: 1:是，0:不是
    """
    weekday = query_date.isoweekday()
    hour = query_date.hour
    print('时间:={0} 星期:={1} 小时:={2}'.format(query_date, weekday, hour))
    if weekday <= 5 and hour >= 9 and hour < 15:
        return 1
    else:
        print('非交易时间')
        return 0


def main(stock_code,count):
    if stock_code is not None:

        # 分时数据-东财
        stock_zh_a_minute_df = ak.stock_zh_a_hist(symbol=stock_code,
                                                  period='daily',
                                                  start_date="20220101",
                                                  end_date="20230414",
                                                  adjust="")
        # print(stock_zh_a_minute_df)
        # 分时数据-新浪
        # stock_zh_a_minute_df = ak.stock_zh_a_minute(symbol=stock_code, period='5', adjust="qfq")
        if stock_zh_a_minute_df is not None:
            # 排序判断,选最近13天
            try:
                data = stock_zh_a_minute_df.sort_values(by='日期', ascending=False).iloc[:13]

                data_list = data.sort_values(by='日期', ascending=True).values.tolist()
                if stock_code == '300025':
                    print(stock_code)
                if len(data_list) >= 13:
                    # for index, item in enumerate(data_list):
                    try:
                        size_list = data_list[0:4]
                        compare_list = data_list[4:13]

                        # 计算size_list的最大值和最小值
                        # 最大值
                        big_value = judge_big_value(size_list)
                        # print("四天最高值："+str(big_value))
                        # 最小值
                        small_value = judge_small_value(size_list)
                        # print("四天最低值："+str(small_value))

                        # 循环判断后九天的最低价是否都低于前四天的最低价，如果是，第14天为买点
                        for index1, item1 in enumerate(compare_list):
                            if float(item1[4]) > float(small_value):
                                break
                            if index1 == len(compare_list) - 1:
                                count = count + 1
                                # strtime = (datetime.datetime.strptime(item1[0], "%Y-%m-%d")
                                #            + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                                # 获取下一个交易日
                                index = datelist.index(item1[0])
                                strtime = datelist[index + 1]
                                str_write = '代码 {0} 日期 {1} 满足神奇九转条件 {2},下一交易日 {3} 为买点 价格:{4} \n'.format(stock_code,
                                                                                                        item1[0], '触底',
                                                                                                        strtime,
                                                                                                        item1[4])
                                Note.write(str_write)  # \n 换行符
                                print(str_write)

                        # 循环判断后九天的最高价是否都高于前四天的最高价，如果是，第14天为卖点
                        for index1, item1 in enumerate(compare_list):
                            if float(item1[3]) < float(big_value):
                                break
                            if index1 == len(compare_list) - 1:
                                count = count + 1
                                # strtime = (datetime.datetime.strptime(item1[0], "%Y-%m-%d")
                                #            + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
                                index = datelist.index(item1[0])
                                strtime = datelist[index + 1]
                                str_write = '代码 {0} 日期 {1} 满足神奇九转条件 {2},下一交易日 {3} 为卖点 价格:{4} \n'.format(stock_code,
                                                                                                        item1[0], '触顶',
                                                                                                        strtime,
                                                                                                        item1[3])
                                Note.write(str_write)  # \n 换行符
                                print(str_write)

                    except IndexError as es:
                        print(stock_code)
                        print(es)
                    except Exception as ess:
                        print(ess)
            except BaseException as ess:
                print(ess)





            # is_up = True
            # is_down = True
            #
            # if len(data_list) > 4:
            #     for index, item in enumerate(data_list[:9]):
            #         # print('时间:{0} ,收盘价:{1},对应前第四个分时的收盘价:{2}'.format(item[0],item[4],data_list[index+4][4]))
            #         # 是否连续九个交易分时都比前面第4交易的收盘价低
            #         if float(item[2]) < float(data_list[index + 4][2]):
            #             is_up = False
            #         # 是否连续九个交易分时都比前面第4交易的收盘价高
            #         if float(item[2]) > float(data_list[index + 4][2]):
            #             is_down = False
            #
            #     # 输出结果
            #     # 假如触底或触顶
            #     if is_up or is_down:
            #         print('分时{0}满足神奇九转条件 {1} 价格:{2}<br/>'.format(item[0], '触顶' if is_up else '触底', item[4]))
            #         # 在这里你可以通过一些第三方手段来通知自己 比如server酱之类的
    return count

def judge_big_value(data_list):
    big_value = None
    for index1 in range(len(data_list)):
        if index1 < len(data_list) - 1:
            if big_value is None:
                flag = data_list[index1][3] >= data_list[index1 + 1][3]
                if flag == True:
                    big_value = data_list[index1][3]
                else:
                    big_value = data_list[index1 + 1][3]
            else:
                flag = big_value >= data_list[index1][3]
                if flag == None:
                    big_value = data_list[index1][3]

    return big_value

def judge_small_value(data_list):
    small_value = None
    for index1 in range(len(data_list)):
        if index1 < len(data_list) - 1:
            if small_value is None:
                flag = data_list[index1][4] <= data_list[index1 + 1][4]
                if flag == True:
                    small_value = data_list[index1][4]
                else:
                    small_value = data_list[index1 + 1][4]
            else:
                flag = small_value <= data_list[index1][4]
                if flag == None:
                    small_value = data_list[index1][4]

    return small_value

def is_demark_dequential(stock_data, date):
    # 判断当前时间节点是否满足神奇九转
    is_up = True
    is_down = True
    stock_data = stock_data[stock_data['day'] < date].sort_values(by='day', ascending=False).iloc[:13].values.tolist()

    if (len(stock_data) < 13):
        return False, False

    for index, item in enumerate(stock_data[:9]):
        # print('时间:{0} ,收盘价:{1},对应前第四个分时的收盘价:{2}'.format(item[0],item[4],stock_data[index+4][4]))
        # 是否连续九个交易分时都比前面第4交易的收盘价低
        if float(item[4]) - 0.001 < float(stock_data[index + 4][4]):
            is_up = False
        # 是否连续九个交易分时都比前面第4交易的收盘价高
        if float(item[4]) + 0.001 > float(stock_data[index + 4][4]):
            is_down = False
    return is_up, is_down


if __name__ == "__main__":
    # 获取正常上市交易的股票
    stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
    print(stock_zh_a_spot_em_df)
    list_codes = []
    for i in [i for i in stock_zh_a_spot_em_df.名称 if i[0] != '*' and i.find('ST') == -1]:
        list_codes.append(stock_zh_a_spot_em_df[stock_zh_a_spot_em_df.名称 == i].代码.values[0])
    count = 0
    for item in list_codes:
        # print('代码' + item)
        if item.find(".") != -1:
            item = item[0 : item.find(".")]
        count = main(item,count)

    Note.close()
    print("模型处理完毕")