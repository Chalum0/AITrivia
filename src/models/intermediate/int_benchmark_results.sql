select
    type,
    lower(trim(difficulty)) as difficulty,
    trim(category) as category,
    question,
    correct_answer,
    incorrect_answers,
    llm_response as ai_answer,
    llm_correct as ai_correct,
    llm_response_instructed as ai_answer_instructed,
    llm_correct_instructed as ai_correct_instructed,
    response_time,

    (
        llm_response is not null
        and trim(llm_response) <> ''
        and llm_correct is not null
    ) as is_evaluated,

    (
        llm_response_instructed is not null
        and trim(llm_response_instructed) <> ''
        and llm_correct_instructed is not null
    ) as is_evaluated_instructed

from {{ ref('stg_questions') }}