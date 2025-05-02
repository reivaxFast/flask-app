import sys

if len(sys.argv) > 1:
    if sys.argv[1] == 'test':
        print("Running tests...")
else:
    print('not riunning tests')
