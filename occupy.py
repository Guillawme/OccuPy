import numpy as np
import pylab as plt
import mrcfile as mf
import os
import sys
import occupy

def main():
    # --------------- INPUT --------------------------------------------------------------------
    plt.ion()
    file_name = sys.argv[1]
    f_open = mf.open(file_name)
    in_data = np.copy(f_open.data)
    nd = np.shape(in_data)
    voxel_size = f_open.voxel_size.x

    # --------------- SETTINGS -----------------------------------------------------------------
    resol = int(3 * 2 * voxel_size)  # Å
    filter_output = None  # Å

    kernel_size = ((int(np.ceil(resol / voxel_size)) // 2) * 2) + 1
    kernel_size = np.clip(kernel_size, 3, 7)
    method = 'percentile_max'
    verbose = False  # True
    levels = 1000
    f_log = open('log.txt', 'w+')
    print(f'Input :\t\t {file_name}', file=f_log)
    print(f'Pixel :\t\t {voxel_size:.2f}', file=f_log)
    print(f'Box   :\t\t {nd}', file=f_log)
    print(f'Kernel:\t\t {kernel_size}', file=f_log)
    print(f'Filter:\t\t {resol}', file=f_log)
    print(f'--------------------------------------------------------------\n', file=f_log)

    # ----- THRESHOLD SETTINGS ---------
    occupancy_threshold = None  # Set to None to estimate using volume-limits
    estimate_occ_threshold = True  # This seems to be a better way than solvent masking to limit solvent boosting

    # ----- MASK SETTINGS ---------
    if len(sys.argv) > 2:
        solvent_mask_name = sys.argv[2] # 1 at solvent. Should be binary.
        s_open = mf.open(solvent_mask_name)
        s_data = np.copy(s_open.data)
    else:
        solvent_mask_name = None
    save_sol_file=True

    # ----- LOW-PASS SETTINGS ---------
    use_lp_for_solvent = False
    use_lp_for_occupancy = True
    use_lp_for_boosting = False

    if use_lp_for_solvent or use_lp_for_occupancy or use_lp_for_boosting:
        lp_data = occupy.map.lowpass_map(in_data, resol, f_open.voxel_size.x, keep_scale=False)
        # print(f'Using low-passed map for some processing, saving file lowpass.mrc.\n',file=f_log)
        occupy.map.new_mrc(lp_data, 'lowpass.mrc', parent=file_name, verbose=False)

    # --------------- DIAGNOSTIC OUTPUT --------------------------------------------------------
    plot = True  # False
    save_occ_file = True
    save_bst_map = False

    # --------------- SOLVENT ESTIMATION -------------------------------------------------------
    if use_lp_for_solvent:
        sol_data = np.copy(lp_data)
    else:
        sol_data = np.copy(in_data)

    # ----- ESTIMATE THRESHOLD ------

    # Estimate solvent paramters for mask
    radius = int(0.95 * nd[0] / 2)
    # print(radius)
    mask = occupy.map.create_circular_mask(nd[0], dim=3, radius=radius)  # TODO use mask radius in Å/nm
    if solvent_mask_name is not None:
        mask = np.array(mask).astype(int) + 1-s_data
        mask = mask > 1.5

    assert sol_data.shape == mask.shape
    h_data = sol_data[mask].flatten()
    sol_limits, sol_param = occupy.solvent.fit_solvent_to_histogram(
        h_data,
        plot=plot,
        n_lev=levels
    )

    if verbose:
        print(f'--------------------------------------------------------------', file=f_log)
        print(f'Detected data limits for solvent:', file=f_log)
        print(f'{sol_limits[0]:.4f} : {sol_limits[1]:.4f} : {sol_limits[2]:.4f} : {sol_limits[3]:.4f}', file=f_log)
        print(f'--------------------------------------------------------------', file=f_log)

    global f, ax1, ax2

    # --------------- OCCUPANCY BOOSTING ------------------------------------------------------

    if use_lp_for_occupancy:
        occ_data = np.copy(lp_data)
    else:
        occ_data = np.copy(in_data)

    if use_lp_for_boosting:
        bst_data = np.copy(lp_data)
    else:
        bst_data = np.copy(in_data)

    boost_kernel = occupy.map.create_circular_mask(kernel_size, dim=3, soft=False)

    occ, full_occ = occupy.occupancy.get_map_occupancy(
        occ_data,
        occ_kernel=boost_kernel,
        sol_threshold=None,  # sol_limits[2],
        save_occ_map=save_occ_file,
        verbose=verbose
    )

    a, b = np.histogram(sol_data[occ > 0.9], bins=levels)
    if plot:
        f = plt.gcf()
        ax1 = f.axes[0]
        ax1.plot(b[:-1], a, 'r', label='high occ')

    # Find intersection of solvent model and content
    solvent_model = occupy.solvent.onecomponent_solvent(b, sol_param[0], sol_param[1], sol_param[2])
    fit = np.clip(solvent_model, 0.0, np.max(solvent_model))
    cond = fit[:-1] > a
    c = len(b) - 2
    while c > 0:
        c -= 1
        if a[c] <= fit[c] and fit[c] > 0.1:
            break

    c = None
    if estimate_occ_threshold and occupancy_threshold is None:
        # occupancy_threshold = (sol_limits[2]+sol_limits[3])/2 / full_occ

        content_fraction_all = np.divide((a + 0.01 - fit[:-1]), a + 0.01)
        solvent_fraction_all = 1 - content_fraction_all

        cond = fit[:-1] > a

        c = len(b) - 2
        while c > 0:
            c -= 1
            if a[c] <= fit[c] and fit[c] > 0.1:
                break
        occupancy_threshold = b[c] / full_occ

    print(f'Detected thresholds:', file=f_log)
    if c is not None:
        print(f'Solvent low : \t {b[c]:.3f}', file=f_log)
    print(f'Solvent full: \t {full_occ:.3f}', file=f_log)
    print(f'Occupancy   : \t {occupancy_threshold:.3f}', file=f_log)

    boosted = occupy.occupancy.boost_map_occupancy(
        bst_data,
        occ,
        occ_threshold=occupancy_threshold,
        save_bst_map=save_bst_map,
        verbose=verbose
    )
    if plot:
        ax1.legend()

    if filter_output is not None:
        rescaled = occupy.map.lowpass_map(boosted, filter_output, voxel_size, keep_scale=True)
    else:
        rescaled = boosted

    new_name = '_' + file_name
    occupy.map.new_mrc(rescaled.astype(np.float32), 'full' + new_name, parent=file_name, verbose=False)
    # print(f'A file with boosted components was written tp full{new_name}',file=f_log)

    if save_occ_file or save_bst_map:
        if verbose:
            print(f'-------------------------------------------------------------- \nAdditional files:', file=f_log)
    if save_occ_file:
        os.rename('occupancy.mrc', 'occ' + new_name)
        if verbose:
            print(f'The occupancy was written to occ{new_name}', file=f_log)
        occupy.map.change_voxel_size('occ' + new_name, parent=file_name)

    if save_bst_map:
        os.rename('boosting.mrc', 'bst' + new_name)
        if verbose:
            print(f'The estimated boosting was written to bst{new_name}', file=f_log)
        occupy.map.change_voxel_size('bst' + new_name, parent=file_name)

    occupy.vis.chimx_viz(
        file_name,
        'full' + new_name,
        'occ' + new_name,
        threshold_ori=sol_limits[3],
        threshold_full=sol_limits[3],
        threshold_occ=occupancy_threshold
    )

    f_open.close()
    f_log.close()


if __name__ == '__main__':
    main()