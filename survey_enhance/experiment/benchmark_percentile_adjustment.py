from survey_enhance.experiment.dataset import (
    dataset,
    calibration_parameters,
    create_frs_dataset,
)
from survey_enhance.experiment.loss.loss import Loss
import torch

initial_loss = Loss(dataset, calibration_parameters)
household_weights = torch.tensor(dataset.household_df.household_weight.values)

from survey_enhance.percentile_matching import (
    match_percentiles_df,
    match_percentiles,
)

VARIABLES_TO_ADJUST = [
    "employment_income",
    "self_employment_income",
    "pension_income",
    "savings_interest_income",
    "dividend_income",
]

from policyengine_uk import Microsimulation, SPI

spi_simulation = Microsimulation(dataset=SPI, dataset_year=2019)

spi_df = spi_simulation.calculate_dataframe(
    VARIABLES_TO_ADJUST + ["age"], period=2019
)
frs_df = dataset.person_df[VARIABLES_TO_ADJUST]
percentile_adjusted_frs_person_df = frs_df.copy()
percentile_adjusted_pensioner_split_frs_person_df = frs_df.copy()
for variable in VARIABLES_TO_ADJUST:
    percentile_adjusted_frs_person_df[variable] = match_percentiles(
        frs_df[variable],
        spi_df[variable],
        percentile_threshold=0.97,
        num_groups=12,
    )

    is_frs_pensioner = dataset.person_df.age >= 65
    is_spi_pensioner = spi_df.age >= 65
    percentile_adjusted_pensioner_split_frs_person_df[variable][
        is_frs_pensioner
    ] = match_percentiles(
        frs_df[variable][is_frs_pensioner],
        spi_df[variable][is_spi_pensioner],
        percentile_threshold=0.97,
        num_groups=12,
    )
    percentile_adjusted_pensioner_split_frs_person_df[variable][
        ~is_frs_pensioner
    ] = match_percentiles(
        frs_df[variable][~is_frs_pensioner],
        spi_df[variable][~is_spi_pensioner],
        percentile_threshold=0.97,
        num_groups=12,
    )


percentile_adjusted_dataset = create_frs_dataset(
    percentile_adjusted_frs_person_df
)
percentile_adjusted_pensioner_split_dataset = create_frs_dataset(
    percentile_adjusted_pensioner_split_frs_person_df
)

dividend_only_percentile_adjusted_dataset = create_frs_dataset(
    percentile_adjusted_frs_person_df[["dividend_income"]]
)

loss = Loss(dataset, calibration_parameters)

frs_loss = loss(household_weights, dataset)
percentile_adjusted_loss = loss(household_weights, percentile_adjusted_dataset)
percentile_adjusted_pensioner_split_loss = loss(
    household_weights, percentile_adjusted_pensioner_split_dataset
)
dividend_only_percentile_adjusted_loss = loss(
    household_weights, dividend_only_percentile_adjusted_dataset
)

print(f"FRS loss: {frs_loss}")
print(f"Percentile adjusted loss: {percentile_adjusted_loss}")
print(
    f"Percentile adjusted pensioner split loss: {percentile_adjusted_pensioner_split_loss}"
)
print(
    f"Dividend only percentile adjusted loss: {dividend_only_percentile_adjusted_loss}"
)
