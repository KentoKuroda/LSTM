# ライブラリの準備
import torch
import torch.nn as nn
from torch import optim
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torch.utils.data import TensorDataset
import torch.nn.utils.rnn as rnn

# GPUチェック
device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
print(device)

from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_absolute_error, mean_squared_error
from sklearn.metrics import confusion_matrix
from sklearn.metrics import classification_report
# import optuna



import csv
import pandas as pd
import os
import random
import numpy as np

from func_LSTM import LSTM
from func_transform_data import transform

'''
from func_CNN import CNN
from func_LSTM import transform
from func_heatmap import make_heatmap
from func_make_graph import make_graph
from func_make_vector import make_vector
from LSTM_percent import count_player
'''


########################################################################################################################################

# data_length
data_length = 9

# grid_size
grid_size_x = 24
grid_size_y = 16

# channel
channel = 3

# data
label_data = 'tactical_action' # tactical_action, time_to_tactical_action

# test か否か
test = True

# val か否か
val = False

# make_graph か否か
make_graph = True
game_id = 3835331
main_team_id = 860

##########################################################################################################################################

if test:
    competition_name = "UEFA_Women's_Euro_2022" # FIFA_World_Cup_2022, UEFA_Euro_2020, UEFA_Women's_Euro_2022, Women's_World_Cup_2023
else:
    competition_name = "FIFA_World_Cup_2022"

print(competition_name)

# data
sequence_data = 'grid_' + str(grid_size_y) + '_' + str(grid_size_x)
print(sequence_data, label_data)

# input size
dim_of_image = (grid_size_y + 2) * (grid_size_x + 2) * channel


# 各戦術的行動の名前 
if label_data != 'attack_or_defense':
    tactical_action_name_list = ['longcounter', 'shortcounter', 'opposition_half_possession', 'own_half_possession', 'counterpressing', 'highpressing', 'middlepressing']
else:
    tactical_action_name_list = ['attack', 'defense']

# 戦術的行動の数
number_of_tactical_action = len(tactical_action_name_list)



def main():


    # シーケンスとラベルをそれぞれ結合(画像ver)
    # connect_data(test, competition_name)
    
    # (B4ver)
    # make_sequence_label()

    # ラベル変更かつ全部同じファイルに
    # label(labels,competition_name)

    # ファイルの長さ
    # file_length = count_file(dir)

    # count_player
    # count_player(dir, file_length)

    # only defense と only no counter を除く
    # sequence_choice(dir, file_length)

    # sequenceの長さ
    # sequence_length(dir, file_length)

    # make graph
    # make_graph(dir_graph)


    # numpy load
    # train
    if test != True:
        sequence_np = np.load("C:\\Users\\kento\\My_Research\\Data\\all_sequence_np\\" + sequence_data + "\\" + competition_name + "\\all_sequence.npy")
        label_np = np.load("C:\\Users\\kento\\My_Research\\Data\\all_label_np\\" + label_data + "\\" + competition_name + "\\all_label.npy", allow_pickle=True)

        sequence_np = transform(sequence_np)

        print(sequence_np.shape, label_np.shape)

        LSTM(sequence_np, label_np, number_of_tactical_action, dim_of_image, test, make_graph, val)
        # CNN(sequence_np, label_np, number_of_player, number_of_tactical_action, test, make_graph, val)
    
    # test
    else:
        # make_graph
        if make_graph:
            
            for i in range(2):

                # 1sthalf
                if i == 0:
                    sequence_np = np.load("C:\\Users\\kento\\My_Research\\Data\\comp_sequence_np\\" + sequence_data + "\\" + competition_name + "\\"+ str(game_id) + "_1sthalf_" + str(main_team_id) + ".npy")
                    label_np = np.load("C:\\Users\\kento\\My_Research\\Data\\comp_label_np\\" + label_data + "\\" + competition_name + "\\"+ str(game_id) + "_1sthalf_" + str(main_team_id) + ".npy", allow_pickle=True)

                    outputs_list, labels_list, len_loader = LSTM(sequence_np, label_np, number_of_tactical_action, dim_of_image, test, make_graph, val)
                    percent_calculate(outputs_list, labels_list, len_loader, test, number_of_tactical_action, make_graph, val, i)

                # 2ndhalf
                else:
                    sequence_np = np.load("C:\\Users\\kento\\My_Research\\Data\\comp_sequence_np\\" + sequence_data + "\\" + competition_name + "\\"+ str(game_id) + "_2ndhalf_" + str(main_team_id) + ".npy")
                    label_np = np.load("C:\\Users\\kento\\My_Research\\Data\\comp_label_np\\" + label_data + "\\" + competition_name + "\\"+ str(game_id) + "_2ndhalf_" + str(main_team_id) + ".npy", allow_pickle=True)

                    outputs_list, labels_list, len_loader = LSTM(sequence_np, label_np, number_of_tactical_action, dim_of_image, test, make_graph, val)
                    percent_calculate(outputs_list, labels_list, len_loader, test, number_of_tactical_action, make_graph, val, i)

        # random_test_data
        else:
            
            sequence_np = np.load("C:\\Users\\kento\\My_Research\\Data\\all_sequence_np\\" + sequence_data + "\\" + competition_name + "\\all_sequence.npy")
            label_np = np.load("C:\\Users\\kento\\My_Research\\Data\\all_label_np\\" + label_data + "\\" + competition_name + "\\all_sequence.npy")

            outputs_list, labels_list, len_loader = LSTM(sequence_np, label_np, number_of_tactical_action, dim_of_image, test, make_graph, val)
            percent_calculate(outputs_list, labels_list, len_loader, test, number_of_tactical_action, make_graph, val)



# modelの評価
def percent_calculate(outputs, labels, length, test, number_of_tactical_action, make_graph, val, half):

    length = len(outputs)
    outputs_np = np.array(outputs)
    labels_np = np.array(labels)

    print('outputs_np:', outputs_np.shape)


    if test:

        '''# optunaによる閾値決定が終わったらメモした値を代入
        # threhold を格納
        threshold = np.zeros(number_of_tactical_action) # 0 人

        threshold[0] = 0.8609294521083235
        threshold[1] = 0.7634105252309301
        threshold[2] = 0.8239291413766827
        threshold[3] = 0.999918004759826'''

        # make_graph
        if make_graph:
            
            # 1sthalf
            if half == 0:
                df_half = pd.read_csv("C:\\Users\\kento\\My_Research\\Data\\df_actions\\" + label_data + "\\" + competition_name + "\\"+ str(game_id) + "_1sthalf_" + str(main_team_id) + ".csv")
            # 2ndhalf
            else:
                df_half = pd.read_csv("C:\\Users\\kento\\My_Research\\Data\\df_actions\\" + label_data + "\\" + competition_name + "\\"+ str(game_id) + "_2ndhalf_" + str(main_team_id) + ".csv")
            
            # 新しいdf
            df_outcome = pd.DataFrame()

            # 結果を入れる列を作成
            for i in range(number_of_tactical_action):
                df_outcome['time_seconds'] = 0
                df_outcome[tactical_action_name_list[i]] = 0
                df_outcome['output_' + tactical_action_name_list[i]] = 0

            # ラベルがついていた回数
            count_label = 0

            # ラベルがついているイベントデータを探し，結果を入れる
            for i in range(len(df_half)):

                if df_half.loc[i, 'label'] == True:

                    if count_label >= length:
                        break

                    df_outcome.loc[count_label, 'time_seconds'] = float(df_half.loc[i, 'time_seconds'])

                    for j in range(number_of_tactical_action):
                        df_outcome.loc[count_label, tactical_action_name_list[j]] = df_half.loc[i, tactical_action_name_list[j]] # 'time_to_' + 
                        df_outcome.loc[count_label, 'output_' + tactical_action_name_list[j]] = outputs_np[count_label, j]

                    count_label += 1


            # 1sthalf
            if half == 0:
                df_outcome.to_csv("C:\\Users\\kento\\My_Research\\Data\\df_outcome\\" + label_data + "\\" + sequence_data + "\\" + competition_name + "\\"+ str(game_id) + "_1sthalf_" + str(main_team_id) + ".csv")
            # 2ndhalf
            else:
                df_outcome.to_csv("C:\\Users\\kento\\My_Research\\Data\\df_outcome\\" + label_data + "\\" + sequence_data + "\\" + competition_name + "\\"+ str(game_id) + "_2ndhalf_" + str(main_team_id) + ".csv")


            '''# 各戦術的行動の正解データの数
            number_of_tactical_action_np = np.zeros(4)

            # 各戦術的行動の正解データの中で認識できた数
            # threshold_1
            recognized_1_tactical_action_np = np.zeros(4)
            # threshold_2
            recognized_2_tactical_action_np = np.zeros(4)


            # 前半の認識精度を計算
            for i in range(4, len(df_half) - 4):

                for j in range(4):

                    # 正解データにおいて, 時間距離0になる時間を探す
                    # longcounter
                    if (df_half.loc[i, ['until_' + tactical_action_name_list[j]]] == 0).any().any():

                        number_of_tactical_action_np[j] += 1

                        # threshold_1
                        for k in range(i - 4, i + 4):

                            if (df_half.loc[k, ['output_until_' + tactical_action_name_list[j]]] <= threshold[j]).any().any():
                                recognized_1_tactical_action_np[j] += 1
                                break


            print(number_of_tactical_action_np)
            print(recognized_1_tactical_action_np)'''

        else:
            if val:
                # optunaによる閾値決定(val)
                # ラベルを０か１に
                longcounter_label_0_or_1_np = labels_np[:,0].astype(np.float32)
                shortcounter_label_0_or_1_np = labels_np[:,1].astype(np.float32)
                opposition_half_possession_label_0_or_1_np = labels_np[:,2].astype(np.float32)
                own_half_possession_label_0_or_1_np = labels_np[:,3].astype(np.float32)

                longcounter_output_0_or_1_np = outputs_np[:,0].astype(np.float32)
                shortcounter_output_0_or_1_np = outputs_np[:,1].astype(np.float32)
                opposition_half_possession_output_0_or_1_np = outputs_np[:,2].astype(np.float32)
                own_half_possession_output_0_or_1_np = outputs_np[:,3].astype(np.float32)

                test_length = length

                for i in range(length):
                        if longcounter_label_0_or_1_np[i] != 1:
                            longcounter_label_0_or_1_np[i] = 0

                        if shortcounter_label_0_or_1_np[i] != 1:
                            shortcounter_label_0_or_1_np[i] = 0

                        if opposition_half_possession_label_0_or_1_np[i] != 1:
                            opposition_half_possession_label_0_or_1_np[i] = 0

                        if own_half_possession_label_0_or_1_np[i] != 1:
                            own_half_possession_label_0_or_1_np[i] = 0

                # threhold を格納
                threshold = np.zeros(number_of_tactical_action)
                
                '''study= optuna.create_study(direction="maximize") 
                study.optimize(objective_longcounter_variable_degree(longcounter_label_0_or_1_np, longcounter_output_0_or_1_np), n_trials = 100)
                print(study.best_params)
                threshold[0] = study.best_params['threshold']

                study = optuna.create_study(direction="maximize") 
                study.optimize(objective_shortcounter_variable_degree(shortcounter_label_0_or_1_np, shortcounter_output_0_or_1_np), n_trials = 100)
                print(study.best_params)
                threshold[1] = study.best_params['threshold']

                study = optuna.create_study(direction="maximize") 
                study.optimize(objective_opposition_half_possession_variable_degree(opposition_half_possession_label_0_or_1_np, opposition_half_possession_output_0_or_1_np), n_trials = 100)
                print(study.best_params)
                threshold[2] = study.best_params['threshold']

                study = optuna.create_study(direction="maximize") 
                study.optimize(objective_own_half_possession_variable_degree(own_half_possession_label_0_or_1_np, own_half_possession_output_0_or_1_np), n_trials = 100)
                print(study.best_params)
                threshold[3] = study.best_params['threshold']'''

                for i in range(number_of_tactical_action):
                    print(threshold[i])


            else:
                # test_dataによる精度評価
                # binarization
                # label
                labels_binarization_np = np.full([length, number_of_tactical_action], 1)
                # 全ての戦術的行動のMAE出すための一次元配列
                all_labels_binarization_np = np.full([length * number_of_tactical_action], 1)
                for i in range(length):
                    for j in range(number_of_tactical_action):
                        if labels_np[i, j] != 1:
                            labels_binarization_np[i, j] = 0
                            all_labels_binarization_np[i * number_of_tactical_action + j] = 0
                        else:
                            labels_binarization_np[i, j] = 1
                            all_labels_binarization_np[i * number_of_tactical_action + j] = 1
                        if labels_np[i, j] != 1:
                            labels_binarization_np[i, j] = 0
                            all_labels_binarization_np[i * number_of_tactical_action + j] = 0

                # output
                outputs_binarization_np = np.full([length, number_of_tactical_action], 1)
                # 全ての戦術的行動のMAE出すための一次元配列
                all_outputs_binarization_np = np.full([length * number_of_tactical_action], 1)
                for i in range(length):
                    for j in range(number_of_tactical_action):
                        if outputs_np[i, j] <= threshold[j]:
                            outputs_binarization_np[i, j] = 0
                            all_outputs_binarization_np[i * number_of_tactical_action + j] = 0
                        else:
                            outputs_binarization_np[i, j] = 1
                            all_outputs_binarization_np[i * number_of_tactical_action + j] = 0
                        if outputs_np[i, j] <= threshold[j]:
                            outputs_binarization_np[i, j] = 0
                            all_outputs_binarization_np[i * number_of_tactical_action + j] = 0

                # 全ての戦術的行動のacc出すための一次元配列
                all_labels_np = np.full([length * number_of_tactical_action], 1)
                all_outputs_np = np.full([length * number_of_tactical_action], 1)
                for i in range(length):
                    for j in range(number_of_tactical_action):
                        all_labels_np[i * number_of_tactical_action + j] = labels_np[i, j]
                        all_outputs_np[i * number_of_tactical_action + j] = outputs_np[i, j]


                for i in range(number_of_tactical_action):
                    print(mean_absolute_error(labels_np[:, i], outputs_np[:, i]))
                print('\n')
                
                for i in range(number_of_tactical_action):
                    print(mean_squared_error(labels_np[:, i], outputs_np[:, i]))
                print('\n')
                
                for i in range(number_of_tactical_action):
                    print(f1_score(labels_binarization_np[:, i], outputs_binarization_np[:, i], pos_label = 0))
                print('\n')

                for i in range(number_of_tactical_action):
                    print(recall_score(labels_binarization_np[:, i], outputs_binarization_np[:, i], pos_label = 0))
                print('\n')

                for i in range(number_of_tactical_action):
                    print(accuracy_score(labels_binarization_np[:, i], outputs_binarization_np[:, i]))



# 閾値付きのrecall
def recall(y_test, y_prob, threshold):

    y_pred = np.zeros(len(y_prob))
    
    for i in range(len(y_prob)):
        if y_prob[i] >= threshold:
            y_pred[i] = 1

        if y_test[i] != 0 and y_test[i] != 1:
            y_test[i] = 0

    # score = recall_score(y_test.astype(int), y_pred.astype(int), pos_label = 0)
    # score = accuracy_score(y_test.astype(int), y_pred.astype(int))
    # score = precision_score(y_test.astype(int), y_pred.astype(int), pos_label = 0)
    score = f1_score(y_test.astype(int), y_pred.astype(int), pos_label = 0)

    return score


# 目的関数
# longcounter
def objective_longcounter_variable_degree(longcounter_label_0_or_1_np, longcounter_output_0_or_1_np):
    def objective_longcounter(trial): 
        threshold = trial.suggest_float('threshold', 0.0, 1.0) # 0~1.0で探索
        ret = recall(longcounter_label_0_or_1_np, longcounter_output_0_or_1_np, threshold)
        return ret
    return objective_longcounter

# shortcounter
def objective_shortcounter_variable_degree(shortcounter_label_0_or_1_np, shortcounter_output_0_or_1_np):
    def objective_shortcounter(trial): 
        threshold = trial.suggest_float('threshold', 0.0, 1.0) # 0~1.0で探索
        ret = recall(shortcounter_label_0_or_1_np, shortcounter_output_0_or_1_np, threshold)
        return ret
    return objective_shortcounter

# opposition_half_possession
def objective_opposition_half_possession_variable_degree(opposition_half_possession_label_0_or_1_np, opposition_half_possession_output_0_or_1_np):
    def objective_opposition_half_possession(trial): 
        threshold = trial.suggest_float('threshold', 0.0, 1.0) # 0~1.0で探索
        ret = recall(opposition_half_possession_label_0_or_1_np, opposition_half_possession_output_0_or_1_np, threshold)
        return ret
    return objective_opposition_half_possession

# own_half_possession
def objective_own_half_possession_variable_degree(own_half_possession_label_0_or_1_np, own_half_possession_output_0_or_1_np):
    def objective_own_half_possession(trial): 
        threshold = trial.suggest_float('threshold', 0.0, 1.0) # 0~1.0で探索
        ret = recall(own_half_possession_label_0_or_1_np, own_half_possession_output_0_or_1_np, threshold)
        return ret
    return objective_own_half_possession



# データにラベルをつける ＆ 同じファイルに番号変えて移動
def label(labels,competition_name):

    # ラベル付与
    i = 0
    for i in range(count_file(labels,competition_name)):
        if i >= 10000:
            break
        df = pd.read_csv("C:\\Users\\黒田堅仁\\OneDrive\\My_Research\\Dataset\\StatsBomb\\segmentation\\add_player\\when_start_point\\counter_possession_others\\sequence\\" + str(competition_name) + "\\" + str(labels) + "\\" + str(i + 1).zfill(6) + ".csv")

        # ファイル移動
        # 前のラベルが何個入ったか
        s = i + 39372
        df.to_csv("C:\\Users\\黒田堅仁\\OneDrive\\My_Research\\Dataset\\StatsBomb\\segmentation\\add_player\\when_start_point\\counter_possession_others\\sequence_choice_42000\\" + str(s + 1).zfill(6) + ".csv")
        
        print(str(s + 1).zfill(6))



# ディレクトリ内のファイル数調査
def count_file(a):# labels,competition_name  or  a  or  competition_name
    # dir = "C:\\Users\\黒田堅仁\\OneDrive\\My_Research\\Dataset\\StatsBomb\\segmentation\\add_player\\when_start_point\\counter_possession_others\\sequence\\" + str(competition_name) + "\\" + str(labels)
    dir = a
    count_file = 0
    
    #ディレクトリの中身分ループ
    for file_name in os.listdir(dir):
    
        #ファイルもしくはディレクトリのパスを取得
        file_path = os.path.join(dir,file_name)
    
        #ファイルであるか判定
        if os.path.isfile(file_path):
            count_file +=1
    
    return count_file



def put_in_seg_data(df, sequence_np, i, number_of_player):

    for j in range(len(df)): # vectorの時は、len(df) - 1


        # 味方の前線 number_of_player/2 人を選ぶ

        # 宣言
        teammate_np = np.full(11, -1.0)
        forward_teammate_np = np.full(int(number_of_player/2), -1.0)

        # 人数確認
        # チームメートの人数11人の時, キーパーがボール保持者だから1人目除いて11人目含む, でも前線から選ぶからキーパーの心配はいらない, 相手の人数11人になることはない.
        if df.at[j, 'teammate_count'] == 0:
            pass

        else:
            # teamamte_np に 11 人のx位置を格納
            for k in range(11):
                teammate_np[k] = df.at[j,'teammate_' + str(k + 1) + '_x']
            
            # 降順に並べ替える
            teammate_np = np.sort(teammate_np)[::-1]

            # forward_teammate_np にnumber_of_player/2人格納
            for k in range(int(number_of_player/2)):
                forward_teammate_np[k] = teammate_np[k]

        
        # 相手のディフェンスライン number_of_player/2 人を選ぶ

        # 宣言
        # keeper は含まない
        opponent_np = np.full(10, -1.0)
        defense_opponent_np = np.full(int(number_of_player/2), -1.0)

        # 人数確認
        if df.at[j, 'opponent_count'] == 0:
            pass

        else:
            # opponent_np に 10 人のx位置を格納
            for k in range(10):
                opponent_np[k] = df.at[j,'opponent_' + str(k + 1) + '_x']
            
            # 降順に並べ替える
            opponent_np = np.sort(opponent_np)[::-1]

            # defense_opponent_np に number_of_player/2 人格納
            for k in range(int(number_of_player/2)):
                defense_opponent_np[k] = opponent_np[k]


        '''# basic (ball_x,y + time)
        sequence_np[i, j, 0] = df.at[j,'start_x']
        sequence_np[i, j, 1] = df.at[j,'start_y']
        sequence_np[i, j, 2] = df.at[j,'time_reset']'''

        # only_x + no_player 
        sequence_np[i, j, 0] = df.at[j,'start_x']
        sequence_np[i, j, 1] = df.at[j,'time_reset']


        '''# only_x + 3_teammate（前線3人）+ 3_opponent（守備3人）
        # only_x + 6_teammate（前線6人）+ 6_opponent（守備6人）
        # only_x + 10_teammate（前線10人）+ 10_opponent（守備10人）
        # teammate
        for l in range(2, 2 + int(number_of_player/2)):
            sequence_np[i, j, l] = forward_teammate_np[l - 2]

        # opponent
        for m in range(2 + int(number_of_player/2), 2 + number_of_player):
            sequence_np[i, j, m] = defense_opponent_np[m - 2 - int(number_of_player/2)]'''


        '''# x + y + tammate_mean + opponent_mean
        sequence_np[i, j, 0] = df.at[j,'start_x']
        sequence_np[i, j, 1] = df.at[j,'start_y']
        sequence_np[i, j, 2] = df.at[j,'time_reset'] # make graphのときのみ time_reset
        sequence_np[i, j, 3] = df.at[j,'teammate_mean_x']
        sequence_np[i, j, 4] = df.at[j,'teammate_mean_y']
        sequence_np[i, j, 5] = df.at[j,'opponent_mean_x']
        sequence_np[i, j, 6] = df.at[j,'opponent_mean_y']'''

        '''# only_x + tammate_mean + opponent_mean
        sequence_np[i, j, 0] = df.at[j,'start_x']
        sequence_np[i, j, 1] = df.at[j,'time_reset']
        sequence_np[i, j, 2] = df.at[j,'teammate_mean_x']
        sequence_np[i, j, 3] = df.at[j,'opponent_mean_x']'''

        '''# ベクトル（初期値なし）
        sequence_np[i, j, 0] = df.at[j,'pass_distance']
        sequence_np[i, j, 1] = df.at[j,'pass_radian']
        sequence_np[i, j, 2] = df.at[j,'pass_time']'''


def put_in_label(df, label_np, i): # 0 ~ 2 の時は + 1

    # 連続値による表現
    # 開始点探索
    label_np[i, 0] = df.at[0, 'until_longcounter']
    label_np[i, 1] = df.at[0, 'until_shortcounter']
    label_np[i, 2] = df.at[0, 'until_opposition_half_possession']
    label_np[i, 3] = df.at[0, 'until_own_half_possession']
    # label_np[i, 4] = df.at[0, 'until_others']
    
    '''# 離散値による表現
    if (df.at[5, 'label'] == 1).any().any():
        label_np[i, 0] = 0
    elif (df.at[5, 'label'] == 2).any().any():
        label_np[i, 1] = 0
    elif (df.at[5, 'label'] == 3).any().any():
        label_np[i, 2] = 0
    elif (df.at[5, 'label'] == 4).any().any():
        label_np[i, 3] = 0'''



def make_sequence_label():

    '''# sequenceのnumpyを作成
    # （ボール + 選手22人）x 2 + 時間 + ラベル = 44
    # sequence_np = np.full([file_length, data_length, number_of_player * 1 + 2], 0.0) # ベクトルの時は、data_length - 1  # only_x の時は * 1 + 2
    # 画像の場合
    # RGB
    # sequence_np = np.zeros([file_length, data_length, grid_size_x, grid_size_y, 3])
    # sequence_np = np.empty((data_length, grid_size_x, grid_size_y, 3), float)
    # gray
    sequence_np = np.empty((file_length, data_length, grid_size_y, grid_size_x), float) # rgbの場合，最後に３，グレーの場合，最後の3を削除

    # labelのnumpyを作成
    label_np = np.full([file_length, number_of_tactical_action], 0.0) # 離散値の場合：１，連続値の場合：0.0

    for i in range(file_length):

        df = pd.read_csv(dir + "\\" + str(i + 1).zfill(6) + ".csv")

        # make_heatmap
        image_sequence_np = make_heatmap(df, data_length, grid_size_x, grid_size_y)
        sequence_np[i] = image_sequence_np
        
        # make_vector
        # make_vector(df)

        # until counter をlabel_npに格納
        # put_in_label(df, label_np, i)

        # put in segmentstion data from df to sequence_np
        # put_in_seg_data(df, sequence_np, i, number_of_player)
        
        # put in attack_sequence data from df to sequence_np
        # put_in_360_data(df, sequence_np, data_length, i)


        # 360 data 整形
        # indentify_player(sequence_np, number_of_player, data_length, i)


        if i % 1000 == 0:
            print(i)
    
    sequence_np = transform(sequence_np, data_variable_list)

    # 転置
    # label_np = label_np.T

    # print(sequence_np)
    # print(label_np)


    # numpy保存
    # train
    if test != True:
        np.save('C:\\Users\\黒田堅仁\\OneDrive\\My_Research\\Dataset\\StatsBomb\\segmentation\\add_player\\when_start_point\\counter_possession_others\\data_42000\\sequence_np\\' + data + '_sequence_np', sequence_np) # test_1_ 0_to_2_ 5000_
        # np.save('C:\\Users\\黒田堅仁\\OneDrive\\My_Research\\Dataset\\StatsBomb\\segmentation\\add_player\\when_start_point\\counter_possession_others\\data_42000\\label_np\\' + data + '_label_np', label_np)
    else:
        np.save("C:\\Users\\黒田堅仁\\OneDrive\\My_Research\\Dataset\\StatsBomb\\segmentation\\add_player\\when_start_point\\counter_possession_others\\data_42000\\test_data\\" + competition + "\\" + data + "_sequence_np", sequence_np) # test_1_ 0_to_2_ 5000_
        np.save("C:\\Users\\黒田堅仁\\OneDrive\\My_Research\\Dataset\\StatsBomb\\segmentation\\add_player\\when_start_point\\counter_possession_others\\data_42000\\test_data\\" + competition + "\\" + data + "_label_np", label_np)
'''



if __name__ == "__main__":
    main()