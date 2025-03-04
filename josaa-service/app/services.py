from typing import Dict, List, Tuple, Optional
import pandas as pd
from .utils import (
    load_data, 
    calculate_admission_probability, 
    get_admission_chances,
    create_probability_plot
)

class JOSAAService:
    def __init__(self):
        self.df = load_data()

    def predict_preferences(
        self,
        jee_rank: int,
        category: str,
        college_type: str,
        preferred_branch: str,
        round_no: str,
        min_probability: float = 0
    ) -> Tuple[List[Dict], Optional[dict]]:
        """Generate college preferences based on input criteria."""
        try:
            if self.df.empty:
                return [], None

            # Apply filters
            df = self.df.copy()
            df["Category"] = df["Category"].str.lower()
            df["Academic Program Name"] = df["Academic Program Name"].str.lower()
            df["College Type"] = df["College Type"].str.upper()
            
            category = category.lower()
            preferred_branch = preferred_branch.lower()
            college_type = college_type.upper()

            if category != "all":
                df = df[df["Category"] == category]
            if college_type != "ALL":
                df = df[df["College Type"] == college_type]
            if preferred_branch != "all":
                df = df[df["Academic Program Name"] == preferred_branch]
            df = df[df["Round"] == str(round_no)]

            if df.empty:
                return [], None

            # Generate college lists
            top_10 = df[
                (df["Opening Rank"] >= jee_rank - 200) &
                (df["Opening Rank"] <= jee_rank)
            ].head(10)

            next_20 = df[
                (df["Opening Rank"] <= jee_rank) &
                (df["Closing Rank"] >= jee_rank)
            ].head(20)

            last_20 = df[
                (df["Closing Rank"] >= jee_rank) &
                (df["Closing Rank"] <= jee_rank + 200)
            ].head(20)

            # Combine results
            final_list = pd.concat([top_10, next_20, last_20]).drop_duplicates()

            # Calculate probabilities
            final_list['Admission Probability (%)'] = final_list.apply(
                lambda x: calculate_admission_probability(
                    jee_rank, 
                    x['Opening Rank'], 
                    x['Closing Rank']
                ),
                axis=1
            )

            final_list['Admission Chances'] = final_list['Admission Probability (%)'].apply(
                get_admission_chances
            )

            # Filter and sort
            final_list = final_list[
                final_list['Admission Probability (%)'] >= min_probability
            ]
            final_list = final_list.sort_values(
                'Admission Probability (%)', 
                ascending=False
            )
            final_list['Preference'] = range(1, len(final_list) + 1)

            # Prepare output
            preferences = final_list[[
                'Preference',
                'Institute',
                'College Type',
                'Location',
                'Academic Program Name',
                'Opening Rank',
                'Closing Rank',
                'Admission Probability (%)',
                'Admission Chances'
            ]].rename(columns={
                'Academic Program Name': 'Branch'
            }).to_dict('records')

            # Generate plot
            plot_data = create_probability_plot(final_list)

            return preferences, plot_data

        except Exception as e:
            print(f"Error in predict_preferences: {str(e)}")
            return [], None
