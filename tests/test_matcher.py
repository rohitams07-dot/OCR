from app.parser.label_matcher import split_label_value


samples = [

    "Last Txn Amount 246.08",

    "Invested Amount 1900",

    "Coupon 17.28",

    "DOB 26-02-04",

    "Email Samir.Bechtelar@yahoo.com",

    "Contact +1xxxxxx1371"

]


for sample in samples:

    label, value = split_label_value(sample)

    print("-" * 40)

    print("INPUT :", sample)

    print("LABEL :", label)

    print("VALUE :", value)