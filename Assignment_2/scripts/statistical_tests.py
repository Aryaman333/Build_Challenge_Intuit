"""Statistical testing utilities for Amazon Products Sales Analysis."""

from scipy import stats
import pandas as pd
import numpy as np


def correlation_test(data, col1, col2):
    """Perform Pearson correlation test."""
    clean_data = data[[col1, col2]].dropna()
    corr, p_value = stats.pearsonr(clean_data[col1], clean_data[col2])
    return {
        'correlation': corr,
        'p_value': p_value,
        'significant': p_value < 0.05
    }


def ttest_independent(data, group_col, value_col, group1_val, group2_val):
    """Perform independent t-test between two groups."""
    group1 = data[data[group_col] == group1_val][value_col].dropna()
    group2 = data[data[group_col] == group2_val][value_col].dropna()
    
    t_stat, p_value = stats.ttest_ind(group1, group2)
    
    return {
        'group1_mean': group1.mean(),
        'group2_mean': group2.mean(),
        't_statistic': t_stat,
        'p_value': p_value,
        'significant': p_value < 0.05
    }


def anova_test(data, group_col, value_col):
    """Perform ANOVA test across multiple groups."""
    groups = [data[data[group_col] == group][value_col].dropna() 
              for group in data[group_col].unique()]
    
    f_stat, p_value = stats.f_oneway(*groups)
    
    return {
        'f_statistic': f_stat,
        'p_value': p_value,
        'significant': p_value < 0.05
    }


def chi_square_test(data, col1, col2):
    """Perform chi-square test for categorical variables."""
    contingency_table = pd.crosstab(data[col1], data[col2])
    chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)
    
    return {
        'chi2_statistic': chi2,
        'p_value': p_value,
        'degrees_of_freedom': dof,
        'significant': p_value < 0.05
    }


def normality_test(data, column):
    """Test for normality using Shapiro-Wilk test."""
    clean_data = data[column].dropna()
    
    if len(clean_data) > 5000:
        sample = clean_data.sample(5000, random_state=42)
    else:
        sample = clean_data
    
    stat, p_value = stats.shapiro(sample)
    
    return {
        'statistic': stat,
        'p_value': p_value,
        'is_normal': p_value > 0.05
    }


def calculate_confidence_interval(data, column, confidence=0.95):
    """Calculate confidence interval for a column."""
    clean_data = data[column].dropna()
    mean = clean_data.mean()
    sem = stats.sem(clean_data)
    ci = stats.t.interval(confidence, len(clean_data)-1, loc=mean, scale=sem)
    
    return {
        'mean': mean,
        'confidence_level': confidence,
        'lower_bound': ci[0],
        'upper_bound': ci[1]
    }


def linear_regression_analysis(data, x_col, y_col):
    """Perform simple linear regression."""
    clean_data = data[[x_col, y_col]].dropna()
    
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        clean_data[x_col], clean_data[y_col]
    )
    
    return {
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_value**2,
        'p_value': p_value,
        'std_error': std_err,
        'significant': p_value < 0.05
    }
