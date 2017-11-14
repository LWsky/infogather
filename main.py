#!/usr/bin/python
# -*- coding:utf-8 -*-

import db
import threading
import argparse

def argparses():
    parameters = dict()
    parser = argparse.ArgumentParser()
    parser.add_argument("-t",help="Gather information interval")
    args = parser.parse_args()
    if args.t:
        parameters["interval"] = args.t
    else:
        parameters["interval"] = 2
    return parameters

def runthread():
    datas = db.DB()
    parameters = argparses()
    all_insert_func = datas.all_func()
    threads = []
    for func in all_insert_func.keys():
        t = threading.Thread(target=all_insert_func[func],args=(int(parameters["interval"]),))
        t.setDaemon(True)
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

if __name__ == '__main__':
    runthread()