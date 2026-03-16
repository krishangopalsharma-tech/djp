from supervisors.models import Supervisor
from .models import SupervisorMovement

def get_daily_movements_logic(target_date):
    """
    Returns a list of Supervisor objects with 'movement' attribute attached.
    Logic includes carrying over previous status if no record exists for target_date.
    """
    supervisors = Supervisor.objects.select_related('depot').all().order_by('name')
    movements = SupervisorMovement.objects.filter(date=target_date).select_related('supervisor', 'look_after')
    movement_map = {m.supervisor.id: m for m in movements}
    
    results = []

    for s in supervisors:
        movement = movement_map.get(s.id)
        if not movement:
            # Try to find last movement to carry over
            last_movement = SupervisorMovement.objects.filter(
                supervisor=s,
                date__lt=target_date
            ).order_by('-date').first()
            
            if last_movement:
                should_copy = False
                new_movement = SupervisorMovement(supervisor=s, date=target_date)
                
                if last_movement.on_leave:
                    if last_movement.leave_to and last_movement.leave_to >= target_date:
                        new_movement.on_leave = True
                        new_movement.leave_from = last_movement.leave_from
                        new_movement.leave_to = last_movement.leave_to
                        new_movement.look_after = last_movement.look_after
                        should_copy = True
                else:
                    # On Duty - carry over location and purpose
                    new_movement.location = last_movement.location
                    new_movement.purpose = last_movement.purpose
                    should_copy = True
                
                if should_copy:
                    movement = new_movement
        
        # Attach to supervisor (or None)
        s.movement = movement
        # If movement is None, we might want a default placeholder in some contexts, 
        # but the View handles None by sending null in JSON.
        # For PDF, we need to handle None.
        
        results.append(s)
        
    return results
