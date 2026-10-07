select
    count(*) as total_questions,

    count(*) filter (where is_evaluated) as evaluated_questions,
    count(*) filter (where not is_evaluated) as unevaluated_questions,
    count(*) filter (where is_evaluated and ai_correct) as correct_answers,

    count(*) filter (where is_evaluated_instructed) as evaluated_questions_instructed,
    count(*) filter (where not is_evaluated_instructed) as unevaluated_questions_instructed,
    count(*) filter (where is_evaluated_instructed and ai_correct_instructed) as correct_answers_instructed,

    100.0 * avg(
        case when is_evaluated
            then cast(ai_correct as integer)
        end
    ) as accuracy_pct,

    100.0 * avg(
        case when is_evaluated_instructed
            then cast(ai_correct_instructed as integer)
        end
    ) as accuracy_pct_instructed,

    count(*) filter (where is_evaluated and is_evaluated_instructed) as paired_questions,

    100.0 * avg(
        case when is_evaluated and is_evaluated_instructed
            then cast(ai_correct as integer)
        end
    ) as accuracy_pct_original_paired,

    100.0 * avg(
        case when is_evaluated and is_evaluated_instructed
            then cast(ai_correct_instructed as integer)
        end
    ) as accuracy_pct_instructed_paired,

    avg(response_time) filter (where is_evaluated and is_evaluated_instructed) as avg_response_time,

    median(response_time) filter (
        where is_evaluated
    ) as median_response_time

from {{ ref('int_benchmark_results') }}