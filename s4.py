# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 15:41:55 2023

@author: 24397
"""

import streamlit as st
import pandas as pd
import numpy as np
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score,mean_squared_error
import seaborn as sns
plt.rcParams['font.family'] = 'SimHei' # 设置字体为SimHei

# 上传文件并选择要使用的列数
uploaded_file = st.file_uploader("上传Excel文件", type="xlsx")
if uploaded_file is not None:
    data = pd.read_excel(uploaded_file)
    input_cols = st.multiselect('请选择输入列', list(data.columns), default=list(data.columns)[:2])
    output_cols = st.multiselect('请选择输出列', list(data.columns), default=list(data.columns)[-1:])
    X = data[input_cols].values
    y = data[output_cols].values
# 数据预处理
    scaler = StandardScaler()
    X_train_raw, X_test_raw, y_train_raw, y_test_raw = train_test_split(data[input_cols].values,
                                                                    data[output_cols].values,
                                                                            test_size=0.2,
                                                                            random_state=None)
    X_train_scaled = scaler.fit_transform(X_train_raw)
    X_test_scaled = scaler.transform(X_test_raw)
    # 调整参数
    hidden_layers = st.slider('隐藏层层数', min_value=1, max_value=10, value=3)
    nodes_list = []
    for i in range(hidden_layers):
        nodes_list.append(st.number_input(f'隐藏层{i+1}节点数', min_value=1, max_value=1000))
    activation = st.selectbox('激励函数', options=['relu', 'logistic', 'tanh','identity'], index=0)
    solver = st.selectbox('优化函数', options=['lbfgs', 'sgd', 'adam'], index=2)
    alpha = st.number_input('正则化系数', value=0.0001)
    learning_rate_init = st.number_input('学习率', value=0.001)
    iterations = st.number_input('迭代次数', value=100)

    # 训练模型
    model = MLPRegressor(hidden_layer_sizes=tuple(nodes_list), activation=activation, solver=solver,
                          alpha=alpha, learning_rate_init=learning_rate_init, max_iter=iterations)
    model.fit(X, y)

   # 训练模型并进行预测
model.fit(X_train_scaled, y_train_raw)
y_pred_raw = model.predict(X_test_scaled)
r2score = r2_score(y_test_raw,y_pred_raw)
mse = mean_squared_error(y_test_raw,y_pred_raw)
import pandas as pd
from sklearn.neural_network import MLPRegressor

# 定义函数来记录 loss
def record_loss(X, y, nodes_list, activation, solver, alpha, learning_rate_init, iterations):
    model = MLPRegressor(hidden_layer_sizes=tuple(nodes_list), activation=activation, solver=solver,
                         alpha=alpha, learning_rate_init=learning_rate_init, max_iter=iterations)
    loss_values = []  # 用于存储每次迭代的 loss 值

    # 定义一个回调函数，在每次迭代后获取 loss 值
    def callback(model, epoch, logs):
        loss = logs.get('loss')
        loss_values.append(loss)

    model.fit(X, y, callbacks=[callback])  # 在训练时使用回调函数

    # 将 loss 值存储到 DataFrame 中
    df = pd.DataFrame(loss_values, columns=['Loss'])

    # 将 DataFrame 存储到 Excel 文件中
    df.to_excel('loss_values.xlsx', index=False)

# 调用函数进行训练和记录 loss
record_loss(X, y, nodes_list, activation, solver, alpha, learning_rate_init, iterations)
# 显示模型评估指标的结果
st.write("## 模型评估")
st.write(f"R2 score: {r2score:.4f}")
st.write(f"均方误差(MSE): {mse:.4f}")
st.write("y:")
st.write(y_test_raw)
st.write("y_pred:")
st.write(y_pred_raw)

# 添加保存按钮
save_button = st.button("保存数据")

if save_button:
    # 将 y 和 y_pred 组合成 DataFrame
    df = pd.DataFrame({'y': y_test_raw.flatten(), 'y_pred': y_pred_raw.flatten()})
    file_name = st.text_input("请输入文件名")
    if file_name:
        df.to_excel(f"{file_name}.xlsx", index=False)
        st.write(f"数据已保存为 {file_name}.xlsx")
  # 展示预测结果和真实值的对比图像
st.write("真实值与预测值的对比图像：")
fig, axs = plt.subplots(len(output_cols), 1, figsize=(6, 4 * len(output_cols)))
if len(output_cols) == 1:
            axs.plot(y_test_raw, label="真实值")
            axs.plot(y_pred_raw, label="预测值")
            axs.set_title("{}".format(output_cols[0]))
            axs.legend()
else:
            for i in range(len(output_cols)):
                axs[i].plot(y_test_raw[:, i], label="真实值")
                axs[i].plot(y_pred_raw[:, i], label="预测值")
                axs[i].set_title("{}".format(output_cols[i]))
                axs[i].legend()
st.pyplot(fig)
