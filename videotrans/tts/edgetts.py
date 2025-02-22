import asyncio
import sys
import time
import os
import edge_tts

from videotrans.configure import config
from videotrans.util import tools

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
else:
    asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())



# Usage
# trimmed_audio = remove_silence_from_end("1.mp3")
# trimmed_audio.export("1_trimmed.mp3", format="mp3")

def get_voice(*, text=None, role=None, rate=None,language=None, filename=None,set_p=True):
    communicate = edge_tts.Communicate(text, role, rate=rate)
    try:
        # print(f'开始配音:{text=},{filename=}')
        asyncio.run(communicate.save(filename))
        # print(f'结束配音:{text=},exists={os.path.exists(filename)}')
        tools.remove_silence_from_end(filename)
        # audio=AudioSegment.from_file(filename, format="mp3")
        # audio[:-100].export(filename,format="mp3")
        # 可能非该类语言，比如英语配音中出现中文等
        if not os.path.exists(filename) or os.path.getsize(filename)<1:
            config.logger.error( f'edgeTTS配音失败:{text=},{filename=}')
            return True
    except Exception as e:
        err = str(e)
        config.logger.error(f'[edgeTTS]{err}')
        if err.find("Invalid response status") > 0 or err.find('WinError 10054')>-1:
            if set_p:
                tools.set_process("edgeTTS过于频繁暂停5s后重试")
            config.settings['dubbing_thread']=1
            time.sleep(10)
            asyncio.run(communicate.save(filename))
        else:
            raise Exception("edgeTTS->"+err)
    return True
