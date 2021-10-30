import pandas as pd
import xgboost as xgb
model2 = xgb.XGBRegressor()
model2.load_model("churnprediction1.json")

var1= 1499
var2= 5
var3= 30
var4= 2061.78
var5=2061.78
var6=5
var7=0
var8=1

predicts = [[var1,var2,var3,var4,var5,var6,var7,var8]]
data = pd.DataFrame(predicts)
predicts2 = model2.predict(data)

predicts3 = predicts2*100

finalna= predicts3.round(2)

lst_str = str(finalna)[1:-1]
print("Predicted Attrition Probability: ", lst_str, "%")
#print(predicts3)


