min = 30001
min2 = 30001
max = -30001
max2 = -30001
a = int(input())
if a == 0:
    min = 0
    min2 = 0
    max = 0
    max2 = 0
while a != 0:
    if (a <= min):
        min2 = min
        min = a
    elif a <= min2:
        min2 = a
    if a >= max:
        max2 = max
        max = a
    elif a >= max2:
        max2 = a
    a = int(input())
print(max+max2)
print(min+min2)
