import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# lookup = [
#     0.1774974536895752,
#     0.21383051156997682,
#     0.21909832239151,
#     0.2488737201690674,
#     0.2783010363578796,
# ]
# trade = [
#     0.10318487167358398,
#     0.1936242092739452,
#     0.2124431589816479,
#     0.20973179015246304,
#     0.20194263207285026,
# ]

# lookup1 = [
#     0.19200640678405761,
#     0.1663171148300171,
#     0.1549901270866394,
#     0.1526965880393982,
#     0.14235296487808227,
# ]

# trade1 = [
#     0,
#     0.17339318139212473,
#     0.19742796897888185,
#     0.19445052411821154,
#     0.19336879085487044,
# ]

# lookup2 = [
#     0.1009301495552063,
#     0.10167068004608154,
#     0.11010745286941528,
#     0.12260974168777466,
#     0.10433539628982544,
# ]


# trade2 = [
#     0,
#     0.050186844433055204,
#     0.060410575168888744,
#     0.05376710210527692,
#     0.0661048854606739,
# ]

lookup3 = [
    0.5192126750946044,
    0.5470261931419372,
    0.5192174935340881,
    0.4975417923927307,
    0.5277837347984314,
]

trade3 = [
    0.5850725514548165,
    0.5625919980822869,
    0.6367299708914249,
    0.6157055263933928,
    0.6307932357398831,
]
# orders = [48, 43, 47, 44, 38]
# orders1 = [0, 20, 22, 53, 68]
orders3 = [40, 51, 43, 44, 47]
p = [0, 0.2, 0.4, 0.6, 0.8]
x = [1, 2, 3, 4, 5]
x_a = np.arange(len(x))

plt.bar(x_a - 0.2, lookup3, 0.4, label="Lookup", align="edge")
plt.bar(x_a + 0.2, trade3, 0.4, label="Trade", align="center")
plt.ylabel("Latency")
plt.xlabel("Lookup vs Trade")
plt.legend()
plt.show()
data = {"client": x, "lookup_time": lookup3, "trade_time": trade3, "orders": orders3}

df = pd.DataFrame(data)

print(df)
