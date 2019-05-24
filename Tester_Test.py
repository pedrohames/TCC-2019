import Tester

my_test = Tester.Tester('10.0.0.1', 'admin', 'admin01', '10.0.0.20')

result = my_test.random_test(0.2, 3000, 4096, band='5G', verbose=False)

print(result)