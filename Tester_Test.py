import Tester

my_test = Tester.Tester('10.0.0.1', 'admin', 'admin01', '10.0.0.2')

# result = my_test.random_test(0.2, 3000, 4096, band='5G', verbose=True)

result = my_test.full_test(3000, 4096, band='5G', verbose=True)

print(result)
