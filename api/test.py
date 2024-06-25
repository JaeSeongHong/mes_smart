
string = "detailData[0][quantity]"

print(string[string.find('][') + 2: -1])
