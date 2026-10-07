select
    difficulty,
    count(*) as total_questions,
    count(*) filter (where is_evaluated) as evaluated_questions,

    100.0 * avg(
        case
            when is_evaluated then cast(ai_correct as integer)
        end
    ) as accuracy_pct,

    avg(response_time) filter (
        where is_evaluated
    ) as avg_response_time

from {{ ref('int_benchmark_results') }}
group by difficulty