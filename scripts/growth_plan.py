#!/usr/bin/env python3
import json, pathlib

HISTORY=pathlib.Path("content/published_history.json")
OUT=pathlib.Path("content/growth_queue.json")

TOPICS=[
    "llegada_del_cachorro","socializacion","rutinas","higiene_y_manejo",
    "paseo_y_correa","llamada","mordisqueo","saltos_y_autocontrol",
    "quedarse_solo","lenguaje_corporal","juego_y_enriquecimiento",
    "sueno_y_descanso","alimentacion_segura","convivencia_con_ninos",
    "convivencia_con_otros_perros","miedos_y_confianza",
    "errores_frecuentes","mitos_caninos","adopcion_responsable",
    "perros_adultos_y_senior"
]
FORMATS=["step_by_step","three_mistakes","before_after","myth_vs_fact","body_language","do_this_not_that","checklist","mini_lesson","problem_solution","three_facts"]
HOOKS=["problem_first","surprising_fact","three_mistakes","unanswered_question","do_this_not_that","before_after","warning_without_alarmism"]

def main():
    history=json.loads(HISTORY.read_text(encoding="utf-8")) if HISTORY.exists() else []
    recent=history[-21:]
    topics={x.get("topic_family") for x in recent}
    formats={x.get("format") for x in recent}
    hooks={x.get("hook_pattern") for x in recent}
    queue=[]
    for topic in TOPICS:
        if topic not in topics:
            queue.append({
                "topic_family":topic,
                "format":next((x for x in FORMATS if x not in formats),"problem_solution"),
                "hook_pattern":next((x for x in HOOKS if x not in hooks),"problem_first")
            })
    OUT.write_text(json.dumps(queue[:14],ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(f"GROWTH_QUEUE={len(queue[:14])}")

if __name__=="__main__":
    main()
