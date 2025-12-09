# clinica/signals.py

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.forms.models import model_to_dict
from .models import Paciente, Parto, RecienNacido, HistorialPaciente

# --- FUNCIÓN AUXILIAR PARA OBTENER USUARIO REAL ---
def get_user_from_instance(instance, default_field_user=None):
    """
    Intenta obtener el usuario que está realizando la acción.
    1. Busca atributo temporal '_usuario_auditoria' inyectado en la Vista.
    2. Si no, usa el usuario guardado en el modelo (default_field_user).
    """
    if hasattr(instance, '_usuario_auditoria') and instance._usuario_auditoria:
        return instance._usuario_auditoria
    return default_field_user

# --- FUNCIÓN AUXILIAR PARA NO REPETIR CÓDIGO ---
def auditar_cambios(instance, modelo_nombre, campos_a_auditar, usuario_responsable, paciente_asociado):
    """
    Compara el estado antiguo con el nuevo y guarda en HistorialPaciente.
    """
    if not hasattr(instance, '_estado_antiguo') or not instance._estado_antiguo:
        return

    estado_nuevo = model_to_dict(instance)
    
    for campo in campos_a_auditar:
        val_ant = str(instance._estado_antiguo.get(campo, ''))
        val_nue = str(estado_nuevo.get(campo, ''))
        
        # Limpieza básica para evitar falsos positivos por None vs ''
        if val_ant == 'None': val_ant = ''
        if val_nue == 'None': val_nue = ''

        if val_ant != val_nue:
            HistorialPaciente.objects.create(
                paciente=paciente_asociado,
                usuario=usuario_responsable,
                campo_modificado=f"{modelo_nombre}: {campo}", # Ej: "RN: peso_gramos"
                valor_anterior=val_ant,
                valor_nuevo=val_nue
            )

# --- CAPTURA DE ESTADO PREVIO (PRE-SAVE) ---

@receiver(pre_save, sender=Paciente)
@receiver(pre_save, sender=Parto)
@receiver(pre_save, sender=RecienNacido)
def capturar_estado_previo(sender, instance, **kwargs):
    if instance.pk:
        try:
            obj_antiguo = sender.objects.get(pk=instance.pk)
            instance._estado_antiguo = model_to_dict(obj_antiguo)
        except sender.DoesNotExist:
            instance._estado_antiguo = None
    else:
        instance._estado_antiguo = None


# --- REGISTRO DE CAMBIOS (POST-SAVE) ---

@receiver(post_save, sender=Paciente)
def audit_paciente(sender, instance, created, **kwargs):
    # Determinamos usuario
    usuario = get_user_from_instance(instance, instance.actualizado_por)
    if created: 
        usuario = instance.registrado_por # Al crear, siempre es registrado_por

    if created:
        HistorialPaciente.objects.create(
            paciente=instance,
            usuario=usuario,
            campo_modificado="CREACIÓN PACIENTE",
            valor_anterior="-",
            valor_nuevo=f"Creado por {instance.registrado_por}"
        )
    else:
        campos = ['nombres', 'apellido_paterno', 'telefono', 'estado_atencion', 'riesgo_obstetrico', 'activo', 'consultorio']
        auditar_cambios(instance, "Paciente", campos, usuario, instance)


@receiver(post_save, sender=Parto)
def audit_parto(sender, instance, created, **kwargs):
    # Determinamos usuario
    usuario = get_user_from_instance(instance, instance.personal_responsable)
    paciente = instance.paciente # La madre

    if created:
        HistorialPaciente.objects.create(
            paciente=paciente,
            usuario=usuario,
            campo_modificado="CREACIÓN PARTO",
            valor_anterior="-",
            valor_nuevo=f"Parto {instance.tipo_parto}"
        )
    else:
        campos = ['fecha_hora', 'tipo_parto', 'sala', 'complicaciones', 'observaciones', 'duracion_trabajo_parto_min']
        auditar_cambios(instance, "Parto", campos, usuario, paciente)


@receiver(post_save, sender=RecienNacido)
def audit_rn(sender, instance, created, **kwargs):
    # Navegamos hacia arriba para hallar a la madre: RN -> Parto -> Paciente
    parto = instance.parto
    paciente = parto.paciente 
    
    # Usuario por defecto: el responsable del parto
    default_user = parto.personal_responsable
    usuario = get_user_from_instance(instance, default_user)

    identificador = instance.identificador or f"RN {instance.pk}"

    if created:
        HistorialPaciente.objects.create(
            paciente=paciente,
            usuario=usuario,
            campo_modificado="NACIMIENTO RN",
            valor_anterior="-",
            valor_nuevo=f"Nace {instance.sexo} ({instance.peso_gramos}g)"
        )
    else:
        campos = ['peso_gramos', 'talla_cm', 'apgar1', 'apgar5', 'reanimacion', 'fecha_control_7_dias']
        auditar_cambios(instance, f"RN ({identificador})", campos, usuario, paciente)