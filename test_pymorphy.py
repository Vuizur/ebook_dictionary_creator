import pymorphy2

morph = pymorphy2.MorphAnalyzer()
results = morph.parse("завершен")
print(results)