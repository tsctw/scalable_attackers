# scalable_attackers
### After training an ocr model
#### Why the model's result is bad when classify the image from backend
The image from backend is base64 format.
We need to transform it to png.
That may cause the image distorted.
When classify the transformed image, we can't get 100% accuracy.
Because the generate method on backend:
```
fill=(
    random.randint(0,200),
    random.randint(0,200),
    random.randint(0,200))
```
```
d.text((40,10), ...)
```

The generate method on attacker:
```
fill=(
    random.randint(100, 200),
    random.randint(100, 200),
    random.randint(100, 200)
)
```

```
text_x = 40
text_y = (height - size) // 2

d.text((40, text_y), ...)
```

The parameters are different. So even if val data get almost 100% accuracy, classify image from backend may have lower performance.
Actually, I tested and the result is really bad.
```
Correct: 371/1000
Accuracy: 0.3710
```