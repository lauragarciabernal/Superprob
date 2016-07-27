from __future__ import print_function, division
import border


if __name__ == "__main__":
    prob = border.laura()

    prob.load_data("/Users/LauraGarcia/Documents/IMEXHS/proba_seg1/fdt_paths.nii.gz")
    prob.start()
