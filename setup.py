from setuptools import setup, find_packages

setup(
	name="udo_stamps",
	version="0.0.1",
	description="Печати и штампы — управление заявками и реестром",
	author="UDO",
	license="MIT",
	packages=find_packages(),
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		"frappe",
	],
)


