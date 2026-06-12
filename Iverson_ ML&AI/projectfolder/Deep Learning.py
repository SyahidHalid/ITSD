import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
print(tf.__version__)
# =====================================================
# STEP 2: Load Dataset
# =====================================================

df = pd.read_csv(".\\pandas\\customer_data.csv")

print("Original Dataset")
print(df)

# =====================================================
# STEP 3: Convert Text to Numbers
# =====================================================

# Neural networks only understand numbers.
# We convert:
#
# Single   -> 1
# Married  -> 0
#
# No  -> 0
# Yes -> 1

marital_encoder = LabelEncoder()
purchase_encoder = LabelEncoder()

df["marital_status"] = marital_encoder.fit_transform(
    df["marital_status"]
)

df["purchase"] = purchase_encoder.fit_transform(
    df["purchase"]
)

print("\nEncoded Dataset")
print(df)

# =====================================================
# STEP 4: Separate Features (X) and Target (y)
# =====================================================

# X = input features
# y = target we want to predict

X = df[["age", "income", "marital_status"]]
y = df["purchase"]

# =====================================================
# STEP 5: Split Training and Testing Data
# =====================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)


scaler = StandardScaler()

X_train = scaler.fit_transform(X_train)
X_Test = scaler.transform(X_test)


model = tf.keras.Sequential([

    #Hidden Layer 1
    tf.keras.layers.Dense(
        units=8,
        activation='relu',
        input_shape=(3,)
    ),

    #Hidden Layer 2
    tf.keras.layers.Dense(
        units=4,
        activation='relu',

    ),

    #Output Layer
    tf.keras.layers.Dense(
        units=1,
        activation='sigmoid',
    )
])
print(model.summary())

#every neuron is an y = mx + c
# y = mx (weight) + c(bias)
# 32 = (3 input * 8 layer) + 8 bias
# 36 = (8 input * 4 layer/neuron) + 4 bias
# 5 = (4 input * 1 layer) + 1 layer

#input = 8
# Neuron  = 4

#Weight  = 8 x 4 = 24
#Bias = 4
#Total = 36

# COmpile the model

model.compile(
    optimizer = 'adam',
    loss="binary_crossentropy",
    metrics = ['accuracy']
)

history = model.fit(
    X_train,
    y_train,
    epochs=50, # Model see the entire training datest one complete time (50)
    batch_size=2, # process them in small group called batches
    validation_split=0.2,
    verbose=1
)

loss, accuracy = model.evaluate(
    X_test,
    y_test,
    verbose=1
)

nc = pd.DataFrame({
    'age': [32],
    'income': [6000],
    'marital_status': ['Single']

})

# Encode marital status
nc["marital_status"] = marital_encoder.transform(
    nc["marital_status"]
)

# Scale features
new_customer_scaled = scaler.transform(nc)

#predic probability
probability = model.predict(new_customer_scaled)
print(probability)

