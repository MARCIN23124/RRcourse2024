import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

# Load the data from the Excel file
file_path = r'C:\Users\marci\Desktop\GIT Materiały\RRcourse2024\11. Metaanalysis\data\metaanalysis_data.xlsx'  # Update with your correct file path
data = pd.read_excel(file_path)

# Calculate the standardized mean differences (effect sizes) for boys and girls playing with 'male' and 'female' toys
data['SE_boys_play_male'] = data['SD_boys_play_male'] / np.sqrt(data['N_boys'])
data['SE_girls_play_male'] = data['SD_girls_play_male'] / np.sqrt(data['N_girls'])

# Pooled variance for meta-analysis
data['Var_boys_play_male'] = data['SE_boys_play_male'] ** 2
data['Var_girls_play_male'] = data['SE_girls_play_male'] ** 2

# Calculate weights for boys and girls
data['Weight_boys'] = 1 / data['Var_boys_play_male']
data['Weight_girls'] = 1 / data['Var_girls_play_male']

# Calculate weighted effect sizes
weighted_effect_boys = (data['Mean_boys_play_male'] * data['Weight_boys']).sum() / data['Weight_boys'].sum()
weighted_effect_girls = (data['Mean_girls_play_male'] * data['Weight_girls']).sum() / data['Weight_girls'].sum()

# Create a funnel plot
plt.figure(figsize=(8, 6))
plt.scatter(data['SE_boys_play_male'], data['Mean_boys_play_male'], color='blue', label='Boys')
plt.scatter(data['SE_girls_play_male'], data['Mean_girls_play_male'], color='red', label='Girls')
plt.axhline(y=weighted_effect_boys, color='blue', linestyle='--', label='Weighted Mean (Boys)')
plt.axhline(y=weighted_effect_girls, color='red', linestyle='--', label='Weighted Mean (Girls)')
plt.xlabel('Standard Error')
plt.ylabel('Mean Time Playing with Male Toys (seconds)')
plt.title('Funnel Plot: Mean Time Playing with Male Toys by Gender')
plt.legend()
plt.show()

# Check if methods / quality affect the results
# Convert quality scores to numerical
quality_factors = ['Case definition adequate', 'Representativeness of cases', 'Selection of controls',
                   'Parental opinion', 'Comparability of both groups', 'Ascertainment of behaviour',
                   'Same ascertainment method for both groups', 'Non‐response rate']

for factor in quality_factors:
    data[factor] = data[factor].apply(lambda x: 1 if x == '*' else 0)

# Correct the formula to handle variable names with spaces
quality_formula = 'Mean_boys_play_male ~ ' + ' + '.join(quality_factors) + ' + C([Parent present]) + C([Neutral toys]) + C(Setting) + Country'

# Run a regression model to check the effect of quality and methods on the effect sizes
model_quality = smf.ols(formula=quality_formula, data=data).fit()
print("Quality and Methods Effect on Boys' Play with Male Toys")
print(model_quality.summary())

# Check if author gender affects the results
data['Female_authors_ratio'] = data['Female authors'] / (data['Female authors'] + data['Male authors'])

author_formula = 'Mean_boys_play_male ~ Female_authors_ratio'
model_author = smf.ols(formula=author_formula, data=data).fit()
print("\nAuthor Gender Effect on Boys' Play with Male Toys")
print(model_author.summary())

#Interpretation of the Regression and Funnel Plot Results:

#The funnel plot depicts the mean time boys and girls spent playing with male-typed toys, plotted against their standard errors. 
#The blue points represent data for boys, and the red points represent data for girls. The dashed lines show the weighted mean 
#times for boys and girls.

#The funnel plot appears relatively symmetrical, suggesting no strong evidence of publication bias. However, there is some spread 
#among the data points, particularly for studies with larger mean times and higher standard errors.

#The regression analysis:
#The coefficient for the female authors' ratio was 94.09, but this was not statistically significant (p-value = 0.438), 
#suggesting that the gender of the authors does not significantly influence the outcome. The low R-squared value (0.024) indicates that the 
#proportion of female authors explains only a small fraction of the variability in the mean time boys spent playing with male-typed toys.

#In conclusion, the funnel plot suggests some variability among the studies but no substantial publication bias. The regression analysis indicates 
#that the gender composition of the authors does not significantly impact the reported outcomes of boys' play preferences.





