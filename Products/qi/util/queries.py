# sql query templates, originally from fixture files, now in source here:

formdates = """
select 
    team.id,
    team.name,
    count(form.measure_id),
    data.itemdate,
    name1.name,
    name2.name,
    max(data.reportdate)
    from 
        sqladmin_team as team,
        sqladmin_formmeasure as form,
        sqladmin_project as project,
        sqladmin_measurementvalue as data
    left join sqladmin_datadate as name1
        on
        name1.period=data.itemdate
        and
        name1.form_id is null
    left join sqladmin_datadate as name2
        on 
        name2.period=data.itemdate
        and
        name2.form_id = %(form_id)i
    where team.id=data.team_id
    and project.id=%(project_id)i
    and team.project_id=%(project_id)i
    and form.form_id=%(form_id)i
    and form.measure_id=data.measure_id
    and team.active IN (true,project.hideinactiveteams)
    
    group by data.itemdate, team.name, name1.name, name2.name, team.id
    order by data.itemdate, team.name;
""".strip()

rosterinfo = """
select 
    team.id,
    form.form_id,
    extract(month from min(data.itemdate))||'/'||extract(year from min(data.itemdate))
        ||'-'||
    extract(month from max(data.itemdate))||'/'||extract(year from max(data.itemdate))
    from sqladmin_team as team,
        sqladmin_formmeasure as form,
        sqladmin_form as forms,
        sqladmin_measurementvalue as data
    where
        data.team_id=team.id
        and 
        data.measure_id=form.measure_id
        and
        team.project_id=%(project_id)s
        and
        forms.id=form.form_id
        and
        forms.project_id=%(project_id)s
    group by team.id, form.form_id;
""".strip()

