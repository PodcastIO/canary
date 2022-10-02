PRJ_DIR=$(cd "$(dirname "$0")";pwd)

cd ${PRJ_DIR}

git pull -r
 
export PYTHONPATH=${PRJ_DIR}/src

#tts --text "喂。" \
#    --model_name "tts_models/zh-CN/baker/tacotron2-DDC-GST" \
#    --vocoder_name "vocoder_models/universal/libri-tts/fullband-melgan" \
#    --out_path /tmp/zh.wav
#
#
#tts --text "Hello!" \
#    --model_name "tts_models/en/sam/tacotron-DDC" \
#    --vocoder_name "vocoder_models/en/sam/hifigan_v2" \
#    --out_path /tmp/en.wav

sh kill.sh

cd ${PYTHONPATH}
nohup python podcast/main.py server >/tmp/server.log 2>&1 &
nohup python podcast/main.py scheduler >/tmp/scheduler.log 2>&1 &
nohup python podcast/main.py rq --name=other >/tmp/other.log 2>&1 &
nohup python podcast/main.py rq --name=zh >/tmp/zh1.log 2>&1 &
nohup python podcast/main.py rq --name=zh >/tmp/zh2.log 2>&1 &
nohup python podcast/main.py rq --name=zh >/tmp/zh3.log 2>&1 &
nohup python podcast/main.py rq --name=en >/tmp/en.log 2>&1 &
nohup python podcast/main.py rq --name=ja >/tmp/ja.log 2>&1 &
