#Test fit function
import numpy as np
import time
import matplotlib.pyplot as plt

x = np.array([0.0, 1.0, 2.0, 3.0,  4.0,  5.0])
y = np.array([0.0, 0.8, 0.9, 0.1, -0.8, -1.0])
z = np.polyfit(x, y, 3)
print z
p = np.poly1d(z)
print p
p(0.5)
print p(0.5)
p30 = np.poly1d(np.polyfit(x, y, 30))

xp = np.linspace(-2, 6, 100)
print xp
plt.plot(x, y, '.', xp, p(xp), '-', xp, p30(xp), '--')
plt.ylim(-2,2)
plt.show()