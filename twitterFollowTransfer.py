# %% [markdown]
# 1. ライブラリのインポート

# %%
import json
import pandas as pd
import tweepy

# %% [markdown]
# 2. jsonファイルからAPIキーとアクセストークンの読込み

# %%
# 旧アカウントの読み込み
with open('twitterOldAccount.json') as f_old:
    oldKeys = json.load(f_old)

# 新アカウントの読み込み
with open('twitterNewAccount.json') as f_new:
    newKeys = json.load(f_new)

# %% [markdown]
# 3. jsonからの読込みを各変数に受け渡し

# %%
# 旧アカウントの読込み受け渡し
old_consumer_key = oldKeys['API_KEY']
old_consumer_secret = oldKeys['API_SECRET_KEY']
old_access_token = oldKeys['ACCESS_TOKEN']
old_access_token_secret = oldKeys['ACCESS_TOKEN_SECRET']

# 新アカウントの読込み受け渡し
new_consumer_key = newKeys['API_KEY']
new_consumer_secret = newKeys['API_SECRET_KEY']
new_access_token = newKeys['ACCESS_TOKEN']
new_access_token_secret = newKeys['ACCESS_TOKEN_SECRET']

# %% [markdown]
# 4. 新旧アカウントのAPIインスタンス作成

# %%
# 旧アカウントでAPIインスタンス作成
old_auth = tweepy.OAuth1UserHandler(old_consumer_key, old_consumer_secret, old_access_token, old_access_token_secret)
old_api = tweepy.API(old_auth, wait_on_rate_limit=True)

# 新アカウントでAPIインスタンス作成
new_auth = tweepy.OAuth1UserHandler(new_consumer_key, new_consumer_secret, new_access_token, new_access_token_secret)
new_api = tweepy.API(new_auth, wait_on_rate_limit=True)

# %% [markdown]
# 5. 旧アカウントでフォローしているアカウントのID、アカウント名、スクリーンネームの取得

# %%
idxList = ['id', 'name', 'screen_name'] # 取得したい属性のリスト
df_oldFollow = pd.DataFrame([], index=idxList) # 旧アカウントでフォローしているアカウントのメタデータ格納用データフレーム
follows = tweepy.Cursor(new_api.get_friends, cursor=-1).items()
for follow in follows:
    record = pd.Series([follow.id, follow.name, follow.screen_name], index=idxList)
    df_oldFollow = pd.concat([df_oldFollow, record], axis=1) # 各アカウントの情報を結合してデータフレーム更新
colNum = df_oldFollow.shape[1]
colList = [i for i in range(colNum)]
df_oldFollow.columns = colList # カラムを0始まりの連番に変更

# %% [markdown]
# 6. 旧アカウントでフォローしているアカウントの中から、新アカウントでフォローするアカウントの選択

# %%
# selector.txtで1/0 (1:フォロー、0:フォローしない) を別テキストファイルで定義
with open('selector.txt', 'r') as f:
    selectList = f.read().split("\n") # 1/0のリスト
selecter = pd.Series(selectList)
df_follow = pd.concat([df_oldFollow.T, selecter], axis=1) # データフレームの結合
df_follow.columns = ['id', 'name', 'screen_name', 'selector'] # 結合後のデータフレームのカラム名更新
# 新アカウントでdf_follow内のselectorが1のユーザーのみ抽出
mask = df_follow['selector'] == str(1)
df_follow = df_follow[mask]

# %% [markdown]
# 7. 選択したアカウントを新アカウントでフォロー

# %%
follow_id = df_follow['id'] # 新アカウントでフォローすると選択したアカウントのID
currentFollows = tweepy.Cursor(new_api.get_friend_ids, cursor=-1).items() # 新アカウントで現在フォロー中のアカウントのIDを取得
id_notFollow = list(set(follow_id) ^ set(currentFollows)) # 選択されたアカウントの中で、まだフォローしていないアカウントのIDのみ取得
for id in id_notFollow:
    user = new_api.create_friendship(user_id=id)

# %%



