project('fontconfig', 'c', version: '2.12.6', license: 'MIT')

compiler = meson.get_compiler('c')

inc = include_directories('.', 'src')

tool_c_args = [
    '-D_ALL_SOURCE=1',
    '-D_GNU_SOURCE=1',
    '-DFLEXIBLE_ARRAY_MEMBER=/**/',
]

fc_case = executable('fc-case', 'fc-case/fc-case.c',
                     c_args: tool_c_args,
                     include_directories: inc,
                     native: true)

fccase_h = custom_target('gen-fccase.h',
                         input : [ 'fc-case/fccase.tmpl.h' ],
                         output : [ 'fccase.h' ],
                         command : [ fc_case, '@INPUT@', '@OUTPUT@', 'fc-case/CaseFolding.txt' ])

fc_lang = executable('fc-lang', [ 'fc-lang/fc-lang.c', fccase_h ],
                     c_args: tool_c_args,
                     include_directories: inc,
                     native: true)

sh = find_program('sh')

thread_dep = dependency('threads', required: false)
freetype_dep = dependency('freetype2')
libxml2_dep = dependency('libxml-2.0', required: false)

deps = [ freetype_dep ]

defines = [
    '-DHAVE_CONFIG_H=1',
]

if host_machine.system() == 'windows'
    defines += [
        '-Dclose=_close'
    ]
    #inc = include_directories('.', 'win')
else
    defines += [
        '-D_ALL_SOURCE=1',
        '-D_GNU_SOURCE=1',
    ]
    #inc = include_directories('.')
endif

cdata = configuration_data()

cdata.set_quoted('VERSION', meson.project_version())
cdata.set('HAVE_WARNING_CPP_DIRECTIVE', 1)
cdata.set('FLEXIBLE_ARRAY_MEMBER', '/**/')
cdata.set('STDC_HEADERS', 1)

if libxml2_dep.found()
    cdata.set('ENABLE_LIBXML2', 1)
    deps += libxml2_dep
endif


code = '''
void memory_barrier (void) { __sync_synchronize (); }
int atomic_add (int *i) { return __sync_fetch_and_add (i, 1); }
int mutex_trylock (int *m) { return __sync_lock_test_and_set (m, 1); }
void mutex_unlock (int *m) { __sync_lock_release (m); }
int main(int argc, char **argv) { return 0; }
'''
if compiler.links(code, name: 'intel atomic primitives test', dependencies: thread_dep)
    cdata.set('HAVE_INTEL_ATOMIC_PRIMITIVES', 1)
endif

check_headers = [
    'dirent.h',
    'ndir.h',
    'dlfcn.h',
    'fcntl.h',
    'inttypes.h',
    'memory.h',
    'stdint.h',
    'stdlib.h',
    'string.h',
    'strings.h',
    'unistd.h',
    'sys/statvfs.h',
    'sys/vfs.h',
    'sys/stat.h',
    'sys/statfs.h',
    'sys/types.h',
    'sys/param.h',
    'sys/mount.h',
]

check_members = [
    ['struct dirent', 'd_type', '#include <dirent.h>'],
    ['struct stat', 'st_mtim', '#include <sys/stat.h>'],
    ['struct statfs', 'f_flags', '#include <sys/statfs.h>'],
]
foreach m: check_members
    if compiler.has_member(m.get(0), m.get(1), prefix: m.get(2))
        def = 'HAVE_' + '_'.join(m.get(0).split(' ')) + '_' + m.get(1)
        def = def.to_upper()
        cdata.set(def, 1)
  endif
endforeach

if compiler.has_member('struct statfs', 'f_flags', prefix: '#include <sys/statfs.h>')
    cdata.set('HAVE_STRUCT_STATFS_', 1)
  # member exists, do whatever is required
endif

foreach h : check_headers
  if compiler.has_header(h)
    h_vec = h.split('.')
    h = '_'.join(h_vec)
    h_vec = h.split('/')
    h = '_'.join(h_vec)
    def = 'HAVE_' + h.to_upper()
    cdata.set(def, 1)
  endif
endforeach

check_funcs = [
    'link',
    'mkstemp',
    'mkostemp',
    '_mktemp_s',
    'mkdtemp',
    'getopt',
    'getopt_long',
    'getpagesize',
    'getprogname',
    'getexecname',
    'rand',
    'random',
    'lrand48',
    'random_r',
    'rand_r',
    'readlink',
    'fstatvfs',
    'fstatfs',
    'lstat',
    'mmap',
    'posix_fadvise',
    'vprintf',
]

foreach f : check_funcs
  if compiler.has_function(f)
    def = 'HAVE_' + f.to_upper()
    cdata.set(def, 1)
  endif
endforeach

check_ft_funcs = [
    'FT_Get_BDF_Property',
    'FT_Get_PS_Font_Info',
    'FT_Has_PS_Glyph_Names',
    'FT_Get_X11_Font_Format'
]
foreach f : check_ft_funcs
  if compiler.has_function(f, dependencies: freetype_dep)
    def = 'HAVE_' + f.to_upper()
    cdata.set(def, 1)
  endif
endforeach

if compiler.has_function('pthread_create', dependencies: thread_dep)
    cdata.set('HAVE_PTHREAD', 1)
    deps += thread_dep
endif

default_fonts = get_option('default_fonts')
if default_fonts == ''
    default_fonts = join_paths(get_option('prefix'), 'share', 'fonts')
endif

cdata.set_quoted('FC_DEFAULT_FONTS', default_fonts)

cdata.set('ALIGNOF_DOUBLE', compiler.alignment('double'))
cdata.set('ALIGNOF_VOID_P', compiler.alignment('void *'))
cdata.set('SIZEOF_VOID_P', compiler.sizeof('void *'))

if get_option('use_iconv')
    cdata.set('USE_ICONV', 1)
    error('FIXME')
else
    cdata.set('USE_ICONV', 0)
endif

wordlist = files('meson-test-wordlist.txt')
fc_gperf_test = run_command(['gperf', '-L', 'ANSI-C', wordlist]).stdout()

code = '''
#include <string.h>

const char *in_word_set(register const char *, register size_t);

''' + fc_gperf_test

if compiler.compiles(code, name : 'gperf check')
    cdata.set('FC_GPERF_SIZE_T', 'size_t')
else
    code = '''
    #include <string.h>

    const char *in_word_set(register const char *, register unsigned int);

    ''' + fc_gperf_test

    if compiler.compiles(code, name : 'gperf check')
        cdata.set('FC_GPERF_SIZE_T', 'unsigned int')
    else
	error('Unable to determine the type of the len parameter of the gperf hash/lookup function')
    endif
endif

template_dir = get_option('template_dir')
if template_dir == ''
    template_dir = join_paths(get_option('prefix'), get_option('datadir'), 'fontconfig', 'conf.avail')
endif
cdata.set_quoted('FC_TEMPLATEDIR', template_dir)

base_config_dir = get_option('base_config_dir')
if base_config_dir == ''
    base_config_dir = join_paths(get_option('prefix'), get_option('sysconfdir'), 'fonts')
endif
cdata.set_quoted('FONTCONFIG_PATH', base_config_dir)

config_dir = get_option('config_dir')
if config_dir == ''
    config_dir = 'conf.d'
endif
cdata.set_quoted('FC_CONFIGDIR', config_dir)

cache_dir = get_option('cache_dir')
if cache_dir == ''
    cache_dir = join_paths(get_option('prefix'), get_option('localstatedir'), 'cache', 'fontconfig')
endif
cdata.set_quoted('FC_CACHEDIR', cache_dir)

configure_file(input: 'config.h.meson', output: 'config.h', configuration: cdata)

fcdata = configuration_data()

fcdata.set_quoted('FC_DEFAULT_FONTS', default_fonts)

add_fonts=''
foreach dir : get_option('add_fonts')
    add_fonts += '<dir>' + dir + '</dir>'
endforeach
fcdata.set('FC_FONTPATH', add_fonts)


fcdata.set_quoted('CONFIGDIR', config_dir)
fcdata.set_quoted('FC_CACHEDIR', cache_dir)
configure_file(input: 'fonts.conf.in', output: 'fonts.conf', configuration: fcdata)



c_src = [
    'src/fcatomic.c',
    'src/fccache.c',
    'src/fccfg.c',
    'src/fccharset.c',
    'src/fccompat.c',
    'src/fcdbg.c',
    'src/fcdefault.c',
    'src/fcdir.c',
    'src/fcformat.c',
    'src/fcfreetype.c',
    'src/fcfs.c',
    'src/fcptrlist.c',
    'src/fcinit.c',
    'src/fclang.c',
    'src/fclist.c',
    'src/fcmatch.c',
    'src/fcmatrix.c',
    'src/fcmutex.h',
    'src/fcname.c',
    'src/fcobjs.c',
    'src/fcpat.c',
    'src/fcrange.c',
    'src/fcserialize.c',
    'src/fcstat.c',
    'src/fcstr.c',
    'src/fcweight.c',
    'src/fcxml.c',
    'src/ftglue.c',
]

ortho = files(
    'fc-lang/aa.orth',
    'fc-lang/ab.orth',
    'fc-lang/af.orth',
    'fc-lang/am.orth',
    'fc-lang/ar.orth',
    'fc-lang/as.orth',
    'fc-lang/ast.orth',
    'fc-lang/av.orth',
    'fc-lang/ay.orth',
    'fc-lang/az_az.orth',
    'fc-lang/az_ir.orth',
    'fc-lang/ba.orth',
    'fc-lang/bm.orth',
    'fc-lang/be.orth',
    'fc-lang/bg.orth',
    'fc-lang/bh.orth',
    'fc-lang/bho.orth',
    'fc-lang/bi.orth',
    'fc-lang/bin.orth',
    'fc-lang/bn.orth',
    'fc-lang/bo.orth',
    'fc-lang/br.orth',
    'fc-lang/bs.orth',
    'fc-lang/bua.orth',
    'fc-lang/ca.orth',
    'fc-lang/ce.orth',
    'fc-lang/ch.orth',
    'fc-lang/chm.orth',
    'fc-lang/chr.orth',
    'fc-lang/co.orth',
    'fc-lang/cs.orth',
    'fc-lang/cu.orth',
    'fc-lang/cv.orth',
    'fc-lang/cy.orth',
    'fc-lang/da.orth',
    'fc-lang/de.orth',
    'fc-lang/dz.orth',
    'fc-lang/el.orth',
    'fc-lang/en.orth',
    'fc-lang/eo.orth',
    'fc-lang/es.orth',
    'fc-lang/et.orth',
    'fc-lang/eu.orth',
    'fc-lang/fa.orth',
    'fc-lang/fi.orth',
    'fc-lang/fj.orth',
    'fc-lang/fo.orth',
    'fc-lang/fr.orth',
    'fc-lang/ff.orth',
    'fc-lang/fur.orth',
    'fc-lang/fy.orth',
    'fc-lang/ga.orth',
    'fc-lang/gd.orth',
    'fc-lang/gez.orth',
    'fc-lang/gl.orth',
    'fc-lang/gn.orth',
    'fc-lang/gu.orth',
    'fc-lang/gv.orth',
    'fc-lang/ha.orth',
    'fc-lang/haw.orth',
    'fc-lang/he.orth',
    'fc-lang/hi.orth',
    'fc-lang/ho.orth',
    'fc-lang/hr.orth',
    'fc-lang/hu.orth',
    'fc-lang/hy.orth',
    'fc-lang/ia.orth',
    'fc-lang/ig.orth',
    'fc-lang/id.orth',
    'fc-lang/ie.orth',
    'fc-lang/ik.orth',
    'fc-lang/io.orth',
    'fc-lang/is.orth',
    'fc-lang/it.orth',
    'fc-lang/iu.orth',
    'fc-lang/ja.orth',
    'fc-lang/ka.orth',
    'fc-lang/kaa.orth',
    'fc-lang/ki.orth',
    'fc-lang/kk.orth',
    'fc-lang/kl.orth',
    'fc-lang/km.orth',
    'fc-lang/kn.orth',
    'fc-lang/ko.orth',
    'fc-lang/kok.orth',
    'fc-lang/ks.orth',
    'fc-lang/ku_am.orth',
    'fc-lang/ku_ir.orth',
    'fc-lang/kum.orth',
    'fc-lang/kv.orth',
    'fc-lang/kw.orth',
    'fc-lang/ky.orth',
    'fc-lang/la.orth',
    'fc-lang/lb.orth',
    'fc-lang/lez.orth',
    'fc-lang/ln.orth',
    'fc-lang/lo.orth',
    'fc-lang/lt.orth',
    'fc-lang/lv.orth',
    'fc-lang/mg.orth',
    'fc-lang/mh.orth',
    'fc-lang/mi.orth',
    'fc-lang/mk.orth',
    'fc-lang/ml.orth',
    'fc-lang/mn_cn.orth',
    'fc-lang/mo.orth',
    'fc-lang/mr.orth',
    'fc-lang/mt.orth',
    'fc-lang/my.orth',
    'fc-lang/nb.orth',
    'fc-lang/nds.orth',
    'fc-lang/ne.orth',
    'fc-lang/nl.orth',
    'fc-lang/nn.orth',
    'fc-lang/no.orth',
    'fc-lang/nr.orth',
    'fc-lang/nso.orth',
    'fc-lang/ny.orth',
    'fc-lang/oc.orth',
    'fc-lang/om.orth',
    'fc-lang/or.orth',
    'fc-lang/os.orth',
    'fc-lang/pa.orth',
    'fc-lang/pl.orth',
    'fc-lang/ps_af.orth',
    'fc-lang/ps_pk.orth',
    'fc-lang/pt.orth',
    'fc-lang/rm.orth',
    'fc-lang/ro.orth',
    'fc-lang/ru.orth',
    'fc-lang/sa.orth',
    'fc-lang/sah.orth',
    'fc-lang/sco.orth',
    'fc-lang/se.orth',
    'fc-lang/sel.orth',
    'fc-lang/sh.orth',
    'fc-lang/shs.orth',
    'fc-lang/si.orth',
    'fc-lang/sk.orth',
    'fc-lang/sl.orth',
    'fc-lang/sm.orth',
    'fc-lang/sma.orth',
    'fc-lang/smj.orth',
    'fc-lang/smn.orth',
    'fc-lang/sms.orth',
    'fc-lang/so.orth',
    'fc-lang/sq.orth',
    'fc-lang/sr.orth',
    'fc-lang/ss.orth',
    'fc-lang/st.orth',
    'fc-lang/sv.orth',
    'fc-lang/sw.orth',
    'fc-lang/syr.orth',
    'fc-lang/ta.orth',
    'fc-lang/te.orth',
    'fc-lang/tg.orth',
    'fc-lang/th.orth',
    'fc-lang/ti_er.orth',
    'fc-lang/ti_et.orth',
    'fc-lang/tig.orth',
    'fc-lang/tk.orth',
    'fc-lang/tl.orth',
    'fc-lang/tn.orth',
    'fc-lang/to.orth',
    'fc-lang/tr.orth',
    'fc-lang/ts.orth',
    'fc-lang/tt.orth',
    'fc-lang/tw.orth',
    'fc-lang/tyv.orth',
    'fc-lang/ug.orth',
    'fc-lang/uk.orth',
    'fc-lang/ur.orth',
    'fc-lang/uz.orth',
    'fc-lang/ve.orth',
    'fc-lang/vi.orth',
    'fc-lang/vo.orth',
    'fc-lang/vot.orth',
    'fc-lang/wa.orth',
    'fc-lang/wen.orth',
    'fc-lang/wo.orth',
    'fc-lang/xh.orth',
    'fc-lang/yap.orth',
    'fc-lang/yi.orth',
    'fc-lang/yo.orth',
    'fc-lang/zh_cn.orth',
    'fc-lang/zh_hk.orth',
    'fc-lang/zh_mo.orth',
    'fc-lang/zh_sg.orth',
    'fc-lang/zh_tw.orth',
    'fc-lang/zu.orth',
    'fc-lang/ak.orth',
    'fc-lang/an.orth',
    'fc-lang/ber_dz.orth',
    'fc-lang/ber_ma.orth',
    'fc-lang/byn.orth',
    'fc-lang/crh.orth',
    'fc-lang/csb.orth',
    'fc-lang/dv.orth',
    'fc-lang/ee.orth',
    'fc-lang/fat.orth',
    'fc-lang/fil.orth',
    'fc-lang/hne.orth',
    'fc-lang/hsb.orth',
    'fc-lang/ht.orth',
    'fc-lang/hz.orth',
    'fc-lang/ii.orth',
    'fc-lang/jv.orth',
    'fc-lang/kab.orth',
    'fc-lang/kj.orth',
    'fc-lang/kr.orth',
    'fc-lang/ku_iq.orth',
    'fc-lang/ku_tr.orth',
    'fc-lang/kwm.orth',
    'fc-lang/lg.orth',
    'fc-lang/li.orth',
    'fc-lang/mai.orth',
    'fc-lang/mn_mn.orth',
    'fc-lang/ms.orth',
    'fc-lang/na.orth',
    'fc-lang/ng.orth',
    'fc-lang/nv.orth',
    'fc-lang/ota.orth',
    'fc-lang/pa_pk.orth',
    'fc-lang/pap_an.orth',
    'fc-lang/pap_aw.orth',
    'fc-lang/qu.orth',
    'fc-lang/quz.orth',
    'fc-lang/rn.orth',
    'fc-lang/rw.orth',
    'fc-lang/sc.orth',
    'fc-lang/sd.orth',
    'fc-lang/sg.orth',
    'fc-lang/sid.orth',
    'fc-lang/sn.orth',
    'fc-lang/su.orth',
    'fc-lang/ty.orth',
    'fc-lang/wal.orth',
    'fc-lang/za.orth',
    'fc-lang/lah.orth',
    'fc-lang/nqo.orth',
    'fc-lang/brx.orth',
    'fc-lang/sat.orth',
    'fc-lang/doi.orth',
    'fc-lang/mni.orth',
)

fclang_h = custom_target('gen-fclang.h',
        input : [ 'fc-lang/fclang.tmpl.h', ortho ],
        output : [ 'fclang.h' ],
        command : [ fc_lang, '@INPUT0@', '@OUTPUT@', ortho ])

public_files = files(
        'fontconfig/fontconfig.h',
        'src/fcdeprecate.h',
        'fontconfig/fcprivate.h')

# XXX: having to hard code path to src directory
makealias = files('src/makealias')
fcalias_h = custom_target('gen-fcalias.h',
        input : [ public_files ] + c_src,
        output : [ 'fcalias.h', 'fcaliastail.h' ],
        command : [ sh, makealias, '../src', '@OUTPUT@', '@INPUT0@' ])

# XXX: having to hard code path to src directory
public_ft_files = files('fontconfig/fcfreetype.h')
fcftalias_h = custom_target('gen-fcftalias.h',
        input : [ public_ft_files ] + c_src,
        output : [ 'fcftalias.h', 'fcftaliastail.h' ],
        command : [ sh, makealias, '../src', '@OUTPUT@', '@INPUT0@' ])

# XXX: this is a hack for now, and won't work when cross-compiling.
#
# Ideally I think Meson would provide some portable way of invoking the c
# compiler to only preprocess a file within a custom target. (not sure how the
# -o argument would be abstracted)
#
# A second issue here seems to be that there isn't an equivalent of files() for
# representing directories, so this hard-codes '-I..' into the command
#
cpp = find_program('gcc', 'clang', 'clang-cl')
fcobjshash_gperf_pre = custom_target('gen-gperf-pre',
        input : [ 'src/fcobjshash.gperf.h', 'src/fcobjs.h' ],
        output : [ 'fcobjshash.gperf.pre' ],
        command : [ cpp, '-E', '-I..', '@INPUT0@', '-o', '@OUTPUT@' ])

makegperf = files('src/makegperf')
fcobjshash_gperf = custom_target('gen-gperf',
        input : fcobjshash_gperf_pre,
        output : [ 'fcobjshash.gperf' ],
        command : [ sh, makegperf, '@INPUT@', '@OUTPUT@' ])

gperf = find_program('gperf')
fcobjshash_h = custom_target('gen-objhash',
        input : fcobjshash_gperf,
        output : [ 'fcobjshash.h' ],
        command : [ gperf, '-m', '100', '@INPUT@', '--output-file', '@OUTPUT@' ])

fc_lib = library('fontconfig', c_src, fclang_h, fcobjshash_h, fcalias_h, fcftalias_h,
        c_args: defines,
        include_directories: inc,
        dependencies: deps)
