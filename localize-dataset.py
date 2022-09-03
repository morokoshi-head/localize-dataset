import argparse
import cv2
import glob
import os
import shutil
import sys
from tqdm import tqdm

LOCALIZE_WIDTH = 480
LOCALIZE_HEIGHT = 270

input_dir = ""
output_dir = ""

def localize_bbox_1d(obj_s, obj_e, crp_s, crp_e, max_size):
    lcl_obj_s = 0
    lcl_obj_e = 0

    if(obj_e <= crp_s):
        lcl_obj_s = 0
        lcl_obj_e = 0

    elif((obj_s < crp_s) and (crp_s <= obj_e)):
        lcl_obj_s = 0
        lcl_obj_e = obj_e - crp_s

    elif((crp_s < obj_s) and (obj_e <= crp_e)):
        lcl_obj_s = obj_s - crp_s
        lcl_obj_e = obj_e - crp_s

    elif((obj_s < crp_e) and (crp_e <= obj_e)):
        lcl_obj_s = obj_s - crp_s
        lcl_obj_e = max_size - 1

    elif((crp_e < obj_s)):
        lcl_obj_s = 0
        lcl_obj_e = 0

    else:
        lcl_obj_s = 0
        lcl_obj_e = 0

    return lcl_obj_s, lcl_obj_e

def main():
    global input_dir
    global output_dir

    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", help="input directory")
    parser.add_argument("output_dir", help="output directory")

    args = parser.parse_args()
    input_dir = args.input_dir
    output_dir = args.output_dir

    if(os.path.exists(output_dir)):
        shutil.rmtree(output_dir)

    os.makedirs(output_dir)

    read_files = glob.glob(os.path.join(input_dir, "*.txt"))

    for read_file in tqdm(read_files):
        img_path = os.path.join(read_file.replace(".txt", ".png"))

        img = cv2.imread(img_path)
        img_h, img_w = img.shape[:2]

        crp_num_x = int(img_w / LOCALIZE_WIDTH)
        crp_num_y = int(img_h / LOCALIZE_HEIGHT)

        with open(read_file, "r") as rf:
            lines = rf.readlines()

            for line in lines:
                line = line.replace("\n", "")
                value = line.split(" ")
    
                obj_class = int(value[0])
                obj_cx = float(value[1]) * img_w
                obj_cy = float(value[2]) * img_h
                obj_w = float(value[3]) * img_w
                obj_h = float(value[4]) * img_h
    
                obj_sx = obj_cx - (obj_w/2.0)
                obj_ex = obj_cx + (obj_w/2.0)
                obj_sy = obj_cy - (obj_h/2.0)
                obj_ey = obj_cy + (obj_h/2.0)
    
                lcl_img_num = 0
                for i in range(crp_num_y):
                    crp_sy = LOCALIZE_HEIGHT * i
                    crp_ey = crp_sy + LOCALIZE_HEIGHT
    
                    lcl_obj_sy, lcl_obj_ey = localize_bbox_1d(obj_sy, obj_ey, crp_sy, crp_ey, LOCALIZE_HEIGHT)
    
                    for j in range(crp_num_x):
                        lcl_img_num += 1
    
                        crp_sx = LOCALIZE_WIDTH * j
                        crp_ex = crp_sx + LOCALIZE_WIDTH
    
                        lcl_obj_sx = 0
                        lcl_obj_ex = LOCALIZE_WIDTH - 1
    
                        lcl_obj_sx, lcl_obj_ex = localize_bbox_1d(obj_sx, obj_ex, crp_sx, crp_ex, LOCALIZE_WIDTH)
    
                        lcl_img = img[crp_sy:crp_ey, crp_sx:crp_ex]
                        lcl_img_name = os.path.basename(img_path).replace(".png", ("_" + str(lcl_img_num) + ".png"))
    
                        cv2.imwrite(os.path.join(output_dir, lcl_img_name), lcl_img)

                        with open(os.path.join(output_dir, lcl_img_name.replace(".png", ".txt")), "a") as wf:
                            if(((lcl_obj_ey - lcl_obj_sy) == 0) or ((lcl_obj_ey - lcl_obj_sy) == 0)):
                                pass
                            else:
                                print(str(obj_class), " ", \
                                      str((lcl_obj_sx+lcl_obj_ex) / (LOCALIZE_WIDTH*2)), " ", \
                                      str((lcl_obj_sy+lcl_obj_ey) / (LOCALIZE_HEIGHT*2)), " ", \
                                      str((lcl_obj_ex-lcl_obj_sx) / LOCALIZE_WIDTH), " ", \
                                      str((lcl_obj_ey-lcl_obj_sy) / LOCALIZE_HEIGHT), file=wf)
    
if __name__ == "__main__":
    main()