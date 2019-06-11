import Tester
import time

start_str_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
start_time = time.time()
print(f'Starting test at: {start_str_time}')

my_test = Tester.Tester('10.0.0.1', 'admin', 'admin01', '10.0.0.2')

resultr = my_test.random_test(0.1, 3000, 4096, band='5G', verbose=True)


# result = my_test.full_test(3000, 4096, band='5G', verbose=True)

finish_time = time.time()
print(f'Total test time:\n {finish_time-start_time}')
# print(result)
