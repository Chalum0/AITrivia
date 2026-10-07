select *
from read_parquet(
    '{{ env_var("AITRIVIA_ROOT") }}/silver/questions.parquet'
)