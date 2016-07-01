#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <errno.h>
#include <string.h>
#include <math.h>
#include "controller.h"
#include "output.h"
#include "init.h"

#include "pythonCon.h"

#ifdef HAVE_MPI
# include <mpi.h>
#endif /* HAVE_MPI */


/**
 * Forces and moments on the embedded solid boundaries.
 * \beginobject{GfsController}
 */

static gboolean vector_read (GtsFile * fp, FttVector * p)
{
  if (fp->type != GTS_INT && fp->type != GTS_FLOAT) {
    gts_file_error (fp, "expecting a number (p.x)");
    return FALSE;
  }
  p->x = atof (fp->token->str);
  gts_file_next_token (fp);

  if (fp->type != GTS_INT && fp->type != GTS_FLOAT) {
    gts_file_error (fp, "expecting a number (p.y)");
    return FALSE;
  }
  p->y = atof (fp->token->str);
  gts_file_next_token (fp);

  if (fp->type != GTS_INT && fp->type != GTS_FLOAT) {
    gts_file_error (fp, "expecting a number (p.z)");
    return FALSE;
  }
  p->z = atof (fp->token->str);
  gts_file_next_token (fp);
  return TRUE;
}

static void gfs_controller_solid_force_destroy (GtsObject * object)
{
  if (GFS_CONTROLLER_SOLID_FORCE (object)->weight)
    gts_object_destroy (GTS_OBJECT (GFS_CONTROLLER_SOLID_FORCE (object)->weight));

  (* GTS_OBJECT_CLASS (gfs_controller_solid_force_class ())->parent_class->destroy) (object);
}

static void gfs_controller_solid_force_read (GtsObject ** o, GtsFile * fp)
{
  GfsControllerSolidForce * l = GFS_CONTROLLER_SOLID_FORCE (*o);

  (* GTS_OBJECT_CLASS (gfs_controller_solid_force_class ())->parent_class->read) (o, fp);
  if (fp->type == GTS_ERROR)
    return;

  if (fp->type != '\n') {
    if (!l->weight)
      l->weight = gfs_function_new (gfs_function_class (), 0.);
    gfs_function_read (l->weight, gfs_object_simulation (l), fp);
  }
}

static void gfs_controller_solid_force_write (GtsObject * o, FILE * fp)
{
  GfsControllerSolidForce * l = GFS_CONTROLLER_SOLID_FORCE (o);
  (* GTS_OBJECT_CLASS (gfs_controller_solid_force_class ())->parent_class->write) (o, fp);
  if (l->weight)
    gfs_function_write (l->weight, fp);
}

static gboolean gfs_controller_solid_force_event (GfsEvent * event, 
					      GfsSimulation * sim)
{
  if ((* GFS_EVENT_CLASS (GTS_OBJECT_CLASS (gfs_controller_solid_force_class ())->parent_class)->event)
      (event, sim) &&
      sim->advection_params.dt > 0.) {
    GfsDomain * domain = GFS_DOMAIN (sim);
    FttVector pf, vf, pm, vm;
    gdouble L = sim->physical_params.L, Ln = pow (L, 3. + FTT_DIMENSION - 2.);

    gfs_domain_solid_force (domain, &pf, &vf, &pm, &vm, GFS_CONTROLLER_SOLID_FORCE (event)->weight);

#ifdef HAVE_MPI
    int world_rank;
    MPI_Comm_rank(MPI_COMM_WORLD, &world_rank);
    g_log (G_LOG_DOMAIN, G_LOG_LEVEL_DEBUG, "[%d] Sending information at time step: %d", world_rank, sim->time.i);
#else
    g_log (G_LOG_DOMAIN, G_LOG_LEVEL_DEBUG, "Sending information at time step: %d", sim->time.i);
#endif
    sendForceValue(pf,vf,pm,vm, sim->time.i, sim->time.t);
     
    return TRUE;
  }
  return FALSE;
}

static void gfs_controller_solid_force_class_init (GfsEventClass * klass)
{
  GTS_OBJECT_CLASS (klass)->read = gfs_controller_solid_force_read;
  GTS_OBJECT_CLASS (klass)->write = gfs_controller_solid_force_write;
  GTS_OBJECT_CLASS (klass)->destroy = gfs_controller_solid_force_destroy;
  GFS_EVENT_CLASS (klass)->event = gfs_controller_solid_force_event;
}

GfsEventClass * gfs_controller_solid_force_class (void)
{
  static GfsEventClass * klass = NULL;

  if (klass == NULL) {
    GtsObjectClassInfo gfs_controller_solid_force_info = {
      "GfsControllerSolidForce",
      sizeof (GfsControllerSolidForce),
      sizeof (GfsEventClass),
      (GtsObjectClassInitFunc) gfs_controller_solid_force_class_init,
      (GtsObjectInitFunc) NULL,
      (GtsArgSetFunc) NULL,
      (GtsArgGetFunc) NULL
    };
    klass = gts_object_class_new (GTS_OBJECT_CLASS (gfs_event_class ()),
				  &gfs_controller_solid_force_info);
  }

  return klass;
}

/** \endobject{GfsController} */


/**
 * Writing the values of variables at specified locations.
 * \beginobject{GfsControllerLocation}
 */

static gchar default_precision[] = "%g";

static void gfs_controller_location_destroy (GtsObject * object)
{
  GfsControllerLocation * l = GFS_CONTROLLER_LOCATION (object);
  g_array_free (l->p, TRUE);
  g_free (l->label);
  if (l->precision != default_precision)
    g_free (l->precision);

  (* GTS_OBJECT_CLASS (gfs_controller_location_class ())->parent_class->destroy) (object);
}

static void gfs_controller_location_read (GtsObject ** o, GtsFile * fp)
{
  GfsControllerLocation * l = GFS_CONTROLLER_LOCATION (*o);

  if (GTS_OBJECT_CLASS (gfs_controller_location_class ())->parent_class->read)
    (* GTS_OBJECT_CLASS (gfs_controller_location_class ())->parent_class->read) 
      (o, fp);
  if (fp->type == GTS_ERROR)
    return;

  if (fp->type == GTS_STRING) {
    FILE * fptr = fopen (fp->token->str, "r");
    GtsFile * fp1;

    if (fptr == NULL) {
      gts_file_error (fp, "cannot open file `%s'", fp->token->str);
      return;
    }
    fp1 = gts_file_new (fptr);
    while (fp1->type != GTS_NONE) {
      FttVector p;
      if (!vector_read (fp1, &p)) {
	gts_file_error (fp, "%s:%d:%d: %s", fp->token->str, fp1->line, fp1->pos, fp1->error);
	return;
      }
      g_array_append_val (l->p, p);
      while (fp1->type == '\n')
	gts_file_next_token (fp1);
    }
    gts_file_destroy (fp1);
    fclose (fptr);
    gts_file_next_token (fp);
  }
  else if (fp->type == '{') {
    fp->scope_max++;
    do
      gts_file_next_token (fp);
    while (fp->type == '\n');
    while (fp->type != GTS_NONE && fp->type != '}') {
      FttVector p;
      if (!vector_read (fp, &p))
	return;
      g_array_append_val (l->p, p);
      while (fp->type == '\n')
	gts_file_next_token (fp);
    }
    if (fp->type != '}') {
      gts_file_error (fp, "expecting a closing brace");
      return;
    }
    fp->scope_max--;
    gts_file_next_token (fp);
  }
  else {
    FttVector p;
    if (!vector_read (fp, &p))
      return;
    g_array_append_val (l->p, p);
  }

  if (fp->type == '{') {
    gchar * label = NULL, * precision = NULL;
    GtsFileVariable var[] = {
      {GTS_STRING, "label", TRUE, &label},
      {GTS_STRING, "precision", TRUE, &precision},
      {GTS_INT,    "interpolate", TRUE, &l->interpolate},
      {GTS_NONE}
    };
    gts_file_assign_variables (fp, var);
    if (fp->type == GTS_ERROR) {
      g_free (label);
      g_free (precision);
      return;
    }

    if (precision != NULL) {
      if (l->precision != default_precision)
	g_free (l->precision);
      l->precision = precision;
    }

    if (label != NULL) {
      g_free (l->label);
      l->label = label;
    }
  }
}

static void gfs_controller_location_write (GtsObject * o, FILE * fp)
{
  GfsControllerLocation * l = GFS_CONTROLLER_LOCATION (o);
  guint i;

  (* GTS_OBJECT_CLASS (gfs_controller_location_class ())->parent_class->write) (o, fp);

  fputs (" {\n", fp);
  gchar * format = g_strdup_printf ("%s %s %s\n", l->precision, l->precision, l->precision);
  for (i = 0; i < l->p->len; i++) {
    FttVector p = g_array_index (l->p, FttVector, i);
    fprintf (fp, format, p.x, p.y, p.z);
  }
  g_free (format);
  fputc ('}', fp);

  if (l->precision != default_precision || l->label) {
    fputs (" {\n", fp);
    if (l->precision != default_precision)
      fprintf (fp, "  precision = %s\n", l->precision);
    if (l->label)
      fprintf (fp, "  label = \"%s\"\n", l->label);
    if (!l->interpolate)
      fputs ("  interpolate = 0\n", fp);
    fputc ('}', fp);
  }
}

static gboolean gfs_controller_location_event (GfsEvent * event, 
					   GfsSimulation * sim)
{
   if ((* GFS_EVENT_CLASS (GTS_OBJECT_CLASS (gfs_controller_location_class ())->parent_class)->event)
      (event, sim)) {
    GfsDomain * domain = GFS_DOMAIN (sim);
    GfsControllerLocation * location = GFS_CONTROLLER_LOCATION (event);
    guint i;

    gchar * pformat = g_strdup_printf ("%s %s %s %s", 
				       location->precision, location->precision, 
				       location->precision, location->precision);
    gchar * vformat = g_strdup_printf (" %s", location->precision);
    for (i = 0; i < location->p->len; i++) {
      FttVector p = g_array_index (location->p, FttVector, i), pm = p;
      gfs_simulation_map (sim, &pm);
      FttCell * cell = gfs_domain_locate (domain, pm, -1, NULL);
      
      if (cell != NULL) {
	GSList * i = domain->variables;
	
	while (i) {
	  GfsVariable * v = i->data;
	  if (v->name){
	  
	    double d = location->interpolate ? 
		gfs_interpolate (cell, pm, v) : GFS_VALUE (cell, v);
    	 
           sendLocationValue(v->name, d, sim->time.i, sim->time.t, p.x,p.y,p.z); 
	  }
	  i = i->next;
	}
      }
    }

    g_free (pformat);
    g_free (vformat);
  }
  return FALSE;
}

static void gfs_controller_location_class_init (GfsEventClass * klass)
{
  GFS_EVENT_CLASS (klass)->event = gfs_controller_location_event;
  GTS_OBJECT_CLASS (klass)->destroy = gfs_controller_location_destroy;
  GTS_OBJECT_CLASS (klass)->read = gfs_controller_location_read;
  GTS_OBJECT_CLASS (klass)->write = gfs_controller_location_write;
}

static void gfs_controller_location_init (GfsControllerLocation * object)
{
  object->p = g_array_new (FALSE, FALSE, sizeof (FttVector));
  object->precision = default_precision;
  object->interpolate = TRUE;
}

GfsEventClass * gfs_controller_location_class (void)
{
  static GfsEventClass * klass = NULL;

  if (klass == NULL) {
    GtsObjectClassInfo gfs_controller_location_info = {
      "GfsControllerLocation",
      sizeof (GfsControllerLocation),
      sizeof (GfsEventClass),
      (GtsObjectClassInitFunc) gfs_controller_location_class_init,
      (GtsObjectInitFunc) gfs_controller_location_init,
      (GtsArgSetFunc) NULL,
      (GtsArgGetFunc) NULL
    };
    klass = gts_object_class_new (GTS_OBJECT_CLASS (gfs_event_class ()),
				  &gfs_controller_location_info);
  }

  return klass;
}

/** \endobject{GfsControllerLocation} */

/* Initialize module */

/* only define gfs_module_name for "official" modules (i.e. those installed in
   GFS_MODULES_DIR) */
const gchar gfs_module_name[] = "controller";
const gchar * g_module_check_init (void);

const gchar * g_module_check_init (void)
{
  gfs_controller_solid_force_class ();
  gfs_controller_location_class ();
  return NULL;
}
