select
    type,
    lower(trim(difficulty)) as difficulty,
    trim(category) as category,
    question,
    correct_answer,
    incorrect_answers,
    llm_response as ai_answer,
    llm_correct as ai_correct,
    response_time,

    (
        llm_response is not null
        and trim(llm_response) <> ''
        and llm_correct is not null
    ) as is_evaluated

from {{ ref('stg_questions') }}