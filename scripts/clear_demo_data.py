"""
clear_demo_data.py

安全的数据库清理脚本（MySQL）
功能：
 - 可选备份（尝试使用 `mysqldump`）
 - 支持完全清空主要表 (`wishes`, `comments`, `likes`, `comment_likes`, `rate_limits`)
 - 或仅删除匹配 `user_uid` 模式的演示用户（默认 `Visitor_%`）

用法示例：

# 交互方式（会提示确认）：
python scripts/clear_demo_data.py --host localhost --user dbuser --password secret --db ourwish_wall --backup --all

# 仅删除 demo 用户（不全部清空）：
python scripts/clear_demo_data.py --host localhost --user dbuser --password secret --db ourwish_wall --pattern "Visitor_%" --backup

注意：
 - 在生产环境执行前务必先备份数据库。即使脚本尝试使用 mysqldump，仍请手动确认备份文件存在且可用。
 - 脚本会在执行危险操作前要求输入确认文本 `YES`。

"""
import argparse
import shutil
import subprocess
import sys
import os
from datetime import datetime

try:
    import pymysql
except Exception as e:
    print('需要 PyMySQL: pip install PyMySQL')
    raise

TABLES_ORDER_TRUNCATE = [
    'comment_likes',
    'likes',
    'comments',
    'wishes',
    'rate_limits'
]

def run_mysqldump(host, user, password, db, port, outpath):
    mysqldump = shutil.which('mysqldump')
    if not mysqldump:
        print('警告：未找到 mysqldump，可跳过备份或手动备份。')
        return False
    cmd = [
        mysqldump,
        '-h', host,
        '-P', str(port),
        '-u', user,
        f"-p{password}",
        db
    ]
    print('Running:', ' '.join(cmd[:4]), '...')
    with open(outpath, 'wb') as f:
        proc = subprocess.Popen(cmd, stdout=f, stderr=subprocess.PIPE)
        _, err = proc.communicate()
        if proc.returncode != 0:
            print('mysqldump failed:', err.decode(errors='ignore'))
            return False
    return True


def confirm_or_exit(prompt_msg):
    print(prompt_msg)
    print("Type 'YES' to proceed:")
    ans = input().strip()
    if ans != 'YES':
        print('Aborted by user.')
        sys.exit(1)


def truncate_all(conn):
    cur = conn.cursor()
    try:
        cur.execute('SET FOREIGN_KEY_CHECKS=0;')
        for t in TABLES_ORDER_TRUNCATE:
            print('Truncating', t)
            cur.execute(f'TRUNCATE TABLE `{t}`;')
        cur.execute('SET FOREIGN_KEY_CHECKS=1;')
        conn.commit()
    finally:
        cur.close()


def delete_by_user_pattern(conn, pattern):
    cur = conn.cursor()
    try:
        # 删除顺序：comment_likes -> likes -> comments -> wishes
        print('Deleting comment_likes for users like', pattern)
        cur.execute('DELETE cl FROM `comment_likes` cl JOIN `comments` c ON cl.comment_id=c.id WHERE c.user_uid LIKE %s;', (pattern,))
        print('Deleting likes for users like', pattern)
        cur.execute('DELETE FROM `likes` WHERE user_uid LIKE %s;', (pattern,))
        print('Deleting comments for users like', pattern)
        cur.execute('DELETE FROM `comments` WHERE user_uid LIKE %s;', (pattern,))
        print('Deleting wishes for users like', pattern)
        cur.execute('DELETE FROM `wishes` WHERE user_uid LIKE %s;', (pattern,))
        conn.commit()
    finally:
        cur.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--host', required=True)
    p.add_argument('--user', required=True)
    p.add_argument('--password', required=True)
    p.add_argument('--db', required=True)
    p.add_argument('--port', type=int, default=3306)
    p.add_argument('--backup', action='store_true', help='尝试用 mysqldump 备份数据库')
    p.add_argument('--all', action='store_true', help='清空所有主要表（危险）')
    p.add_argument('--pattern', default=None, help='按 user_uid 模式删除（SQL LIKE 语法），例如 "Visitor_%%"')
    p.add_argument('--no-confirm', action='store_true', help='跳过确认（危险）')
    args = p.parse_args()

    if not args.all and not args.pattern:
        print('必须指定 --all 或 --pattern，避免误删全部数据。')
        sys.exit(1)

    # Backup if requested
    if args.backup:
        timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
        out = f'./ourwish_wall_backup_{timestamp}.sql'
        ok = run_mysqldump(args.host, args.user, args.password, args.db, args.port, out)
        if ok:
            print('备份已写入', out)
        else:
            print('备份失败或未执行，继续前请确认是否继续。')

    # Confirmation
    if not args.no_confirm:
        warn = '你即将对数据库执行破坏性操作。'
        if args.all:
            warn += ' 这将清空以下表: ' + ','.join(TABLES_ORDER_TRUNCATE)
        else:
            warn += f" 将删除 user_uid LIKE '{args.pattern}' 的相关数据。"
        confirm_or_exit(warn)

    # Connect
    try:
        conn = pymysql.connect(host=args.host, user=args.user, password=args.password, db=args.db, port=args.port, charset='utf8mb4')
    except Exception as e:
        print('无法连接到数据库:', e)
        sys.exit(1)

    try:
        if args.all:
            truncate_all(conn)
        else:
            delete_by_user_pattern(conn, args.pattern)
        print('操作完成。')
    except Exception as e:
        print('操作发生错误，回滚并退出:', e)
        try:
            conn.rollback()
        except:
            pass
        sys.exit(1)
    finally:
        conn.close()


if __name__ == '__main__':
    main()
