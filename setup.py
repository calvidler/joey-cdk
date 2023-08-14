import setuptools


with open("README.md") as fp:
    long_description = fp.read()


setuptools.setup(
    name="Joey Books Website",
    version="0.0.1",

    description="Joey Books Backend CDK",
    long_description=long_description,
    long_description_content_type="text/markdown",

    author="Callum Vidler",
    author_email="hello@readwithjoey.com",

    package_dir={"": "joey_cdk"},
    packages=setuptools.find_packages(where="joey_cdk"),

    install_requires=[
        "aws-cdk-lib==2.91.0",
        "constructs>=10.0.0,<11.0.0",
        "aws-psycopg2",
        "GitPython",
        "boto3"
    ],

    python_requires=">=3.8",

    classifiers=[
    ],
)
