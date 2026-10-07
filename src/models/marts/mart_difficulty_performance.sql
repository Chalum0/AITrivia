select
    difficulty,
    count(*) as total_questions,

    count(*) filter (where is_evaluated) as evaluated_questions,
    count(*) filter (where is_evaluated_instructed) as evaluated_questions_instructed,

    100.0 * avg(
        case when is_evaluated then cast(ai_correct as integer) end
    ) as accuracy_pct,

    100.0 * avg(
        case when is_evaluated_instructed
            then cast(ai_correct_instructed as integer)
        end
    ) as accuracy_pct_instructed,

    avg(response_time) filter (
        where is_evaluated and is_evaluated_instructed
    ) as avg_response_time

from {{ ref('int_benchmark_results') }}
group by difficulty