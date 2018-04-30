src = [
    'fcatomic.c',
    'fccache.c',
    'fccfg.c',
    'fccharset.c',
    'fccompat.c',
    'fcdbg.c',
    'fcdefault.c',
    'fcdir.c',
    'fcformat.c',
    'fcfreetype.c',
    'fcfs.c',
    'fcptrlist.c',
    'fcinit.c',
    'fclang.c',
    'fclist.c',
    'fcmatch.c',
    'fcmatrix.c',
    'fcmutex.h',
    'fcname.c',
    'fcobjs.c',
    'fcpat.c',
    'fcrange.c',
    'fcserialize.c',
    'fcstat.c',
    'fcstr.c',
    'fcweight.c',
    'fcxml.c',
    'ftglue.c',
]

# XXX: makealias uses hack to resolve absolute path to src/ directory
makealias = files('makealias')

fcalias_h = custom_target('gen-fcalias.h',
        input : [ public_files ] + src,
        output : [ 'fcalias.h', 'fcaliastail.h' ],
        command : [ sh, makealias, '.', '@OUTPUT@', public_files ])

fcftalias_h = custom_target('gen-fcftalias.h',
        input : [ public_ft_files ] + src,
        output : [ 'fcftalias.h', 'fcftaliastail.h' ],
        command : [ sh, makealias, '.', '@OUTPUT@', public_ft_files ])

# XXX: this is a hack for now, and won't work when cross-compiling.
#
# Ideally I think Meson would provide some portable way of invoking the c
# compiler to only preprocess a file within a custom target. (not sure how the
# -o argument would be abstracted)
#
cpp = find_program('gcc', 'clang', 'clang-cl')
fc_top_src = join_paths(meson.source_root(),
                        meson.current_source_dir(),
                        '..')
fcobjshash_gperf_pre = custom_target('gen-gperf-pre',
        input : [ 'fcobjshash.gperf.h', 'fcobjs.h' ],
        output : [ 'fcobjshash.gperf.pre' ],
        command : [ cpp, '-E', '-I' + fc_top_src, '@INPUT0@', '-o', '@OUTPUT@' ])

makegperf = files('makegperf.py')
fcobjshash_gperf = custom_target('gen-gperf',
        input : fcobjshash_gperf_pre,
        output : [ 'fcobjshash.gperf' ],
        command : [ makegperf, '@INPUT@', '@OUTPUT@' ])

gperf = find_program('gperf')
fcobjshash_h = custom_target('gen-objhash',
        input : fcobjshash_gperf,
        output : [ 'fcobjshash.h' ],
        command : [ gperf, '-m', '100', fcobjshash_gperf, '--output-file', '@OUTPUT@' ])

fc_lib = library('fontconfig', src, fclang_h, fcobjshash_h, fcalias_h, fcftalias_h,
        c_args: defines,
        include_directories: inc,
        dependencies: deps)
