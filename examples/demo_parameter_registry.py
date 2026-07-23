from acf.core.default_parameters import create_registry

registry = create_registry()

print()

print("Registered Parameters")

print("----------------------")

for parameter in registry.all():

    print(

        parameter.id,

        parameter.name,

        parameter.units,

        parameter.renderer

    )
