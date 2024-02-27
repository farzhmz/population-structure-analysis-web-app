import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO

def calculate_pairwise_fst(data, output_file_path='Pop_diff_result/pairwise_fst.txt'):
    # Create a dictionary to store allele frequencies for each population
    allele_freqs = {}

    # Separate allele frequencies by SNP and population
    for snp, pop, rf, af in data:
        if snp not in allele_freqs:
            allele_freqs[snp] = {}
        if pop not in allele_freqs[snp]:
            allele_freqs[snp][pop] = {'RF': [], 'AF': []}
        allele_freqs[snp][pop]['RF'].append(rf)
        allele_freqs[snp][pop]['AF'].append(af)

    # Create a DataFrame to store pairwise FST values
    populations = list(allele_freqs[next(iter(allele_freqs))].keys())
    pairwise_fst_matrix = pd.DataFrame(index=populations, columns=populations)

    # Iterate over population pairs
    for i in range(len(populations)):
        for j in range(i + 1, len(populations)):
            pop1 = populations[i]
            pop2 = populations[j]

            # Initialize lists to store FST values for each SNP
            fst_values = []

            # Iterate over SNPs
            for snp, freqs in allele_freqs.items():
                # Calculate average ref and alt frequencies across all populations for the current SNP
                avg_rf = sum(freqs[pop]['RF'][0] for pop in populations) / len(populations)
                avg_af = sum(freqs[pop]['AF'][0] for pop in populations) / len(populations)

                # Calculate Ht
                ht = 2 * avg_rf * avg_af

                # Calculate Hs for each population in the pair
                hs_pop1 = 2 * freqs[pop1]['RF'][0] * freqs[pop1]['AF'][0]
                hs_pop2 = 2 * freqs[pop2]['RF'][0] * freqs[pop2]['AF'][0]
                hs = (hs_pop1 + hs_pop2) / 2

                # Calculate pairwise FST
                if ht == 0:
                    fst = np.nan
                else:
                    fst = (ht - hs) / ht

                fst_values.append(fst)

            # Average FST values across all SNPs for the current pair of populations
            avg_fst = np.nanmean(fst_values)

            # Store the average FST value in the matrix
            pairwise_fst_matrix.at[pop1, pop2] = avg_fst
            pairwise_fst_matrix.at[pop2, pop1] = avg_fst

    # Plot the heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(pairwise_fst_matrix.astype(float), annot=True, cmap="viridis", linewidths=.5, fmt=".3f")
    plt.title('Pairwise FST Matrix')
    
    img_buf = BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)

    # Encode the image as base64
    img_base64 = base64.b64encode(img_buf.read()).decode('utf-8')

    # Close the plot to avoid displaying it
    plt.close()

    # Save pairwise FST values to a text file
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory of the current script (app.py)
    print("Current Script Directory:", current_dir)

    # Output file path modification
    output_file_path = os.path.join(current_dir, 'Pop_diff_result', 'pairwise_fst.txt')
    print("Final Output File Path:", output_file_path)

    # Check if the 'Pop_diff_result' directory exists, if not, create it
    result_dir = os.path.dirname(output_file_path)
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)



    # Save the file
    pairwise_fst_matrix.to_csv(output_file_path, sep='\t', float_format='%.3f')

    # Return the pairwise FST matrix heatmap, text file to static directory and file path in variable(used for download link)
    return pairwise_fst_matrix, img_base64, output_file_path




#data = [("rs1", "JPN", 0.9, 0.1),("rs1", "UK", 1.0, 0.0)]

#Matrix, img, filepath = calculate_pairwise_fst(data)

#print(img)
#print(filepath)



