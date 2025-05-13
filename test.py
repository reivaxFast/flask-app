import databases, inspect

module_name = databases.__name__

defined_classes = [
    obj for name, obj in inspect.getmembers(databases, inspect.isclass)
    if obj.__module__ == module_name
]

print(f"Classes defined in '{module_name}':")
print(defined_classes)