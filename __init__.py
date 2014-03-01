"""`gcccov`

Tool specific initialization for gcccov.
"""

#
# Copyright (c) 2014 by Pawel Tomulik
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE

__docformat__ = "restructuredText"

class _null(object): pass

class GCovRecursionError(Exception): pass

class _GCovAwareObjectEmitter(object):
    """gcov aware object emitter

    This is an emitter object we inject into Object file builders to generate
    propet dependencies between object files and gcov's *.gcno/*.gcda files.
    For each created object this emitter adds its associated *.gcno file to
    object's side effects and *.gcda file to its dependencies.

    The emitter uses the following construction variables:

    - ``GCCCOV_GCNO_SUFFIX``
    - ``GCCCOV_GCDA_SUFFIX``
    - ``GCCCOV_EXCLUDE``,
    - ``GCCCOV_NOCLEAN``,
    - ``GCCCOV_NOIGNORE``.

    The emitter may be injected to default object builders with
    ``GCovInjectObjectEmitters()`` method.
    """
    def __init__(self, original_emitter):
        """Initialize object

        :Parameters:
            original_emitter : object
                original emitter that will be replaced with this object.
        """
        self.original_emitter = original_emitter

    def __call__(self, target, source, env):
        """Actual emitter function"""
        import os
        from SCons.Util import NodeList
        # TODO: test it with variant builds (source and target paths)
        # FIXME: I'm not sure if target[0] is the only relevant node ...
        excludes = env.get('GCCCOV_EXCLUDE',[])
        excludes = env.arg2nodes(excludes, target = target, source = source)
        noclean = env.get('GCCCOV_NOCLEAN',[])
        noclean = env.arg2nodes(noclean, target = target, source = source)
        noignore = env.get('GCCCOV_NOIGNORE',[])
        noignore = env.arg2nodes(noignore, target = target, source = source)
        tgt = target[0]
        tgt_base = os.path.splitext(str(tgt))[0]
        if tgt not in excludes:
            gcno = env.File(tgt_base + env.get('GCCCOV_GCNO_SUFFIX','.gcno'))
            gcda = env.File(tgt_base + env.get('GCCCOV_GCDA_SUFFIX','.gcda'))
            if gcno not in excludes:
                env.SideEffect(gcno, tgt)
                if gcno not in noclean:
                    env.Clean(tgt, gcno)
                if gcno not in noignore:
                    env.Ignore('.', gcno)
            if gcda not in excludes:
                env.Depends(gcda, tgt)
                if gcda not in noclean:
                    env.Clean(tgt, gcda)
                if gcda not in noignore:
                    env.Ignore('.', gcda)
        if self.original_emitter is not None:
            return self.original_emitter(target, source, env)
        else:
            return target, source

def _arg2builder(env, arg):
    """Convert an argument to a builder object it refers.

    :Parameters:
        env: SCons.Environment.Environment
            a SCons Environment object
        arg:
            an argument to be converted to a real builder, may be builder name
            or a builder object.

    What we need in several places of this tool is a builder which has an
    emitter. The user, however, will likely provide just a builder's name, not
    the builder object. The purpose of this function is to resolve these names
    to real builder objects. It also unwraps any CompositeBuilders and so
    on so the returned object is an instance of SCons.Builder.BuilderBase.
    """
    from SCons.Util import is_String
    import SCons.Builder
    if is_String(arg):
        arg = env['BUILDERS'].get(arg)
        if arg is None:
            return arg
    if not isinstance(arg, SCons.Builder.BuilderBase):
        try:
            arg = arg.builder
        except AttributeError:
            arg = None
    return arg

def _arg2builders(env, arg):
    """Convert an argument to a list of builder objects it refers to.

    :Parameters:
        env: SCons.Environment.Environment
            a SCons Environment object
        arg:
            an argument to be converted to a builders, may be builder name,
            builder object or a list of (intermixed) builder names/objects.

    The returned list contains no repetitions (objects are unique).
    """
    from SCons.Util import is_List, uniquer
    if not is_List(arg):
        arg = [ arg ]
    # Make it unique (but preserve order)
    # uniquer() is in SCons since 1.0.0 so it should be fine
    arg = uniquer(arg)
    builders = map(lambda b : _arg2builder(env,b), arg)
    return [b for b in builders if b is not None]

def _get_object_builders(env):
    """Return a list of object builders according to ``env['GCCCOV_OBJECT_BUILDERS']``.

    :Parameters:
        env: SCons.Environment.Environment
            a SCons Environment object
    """
    return _arg2builders(env, env.get('GCCCOV_OBJECT_BUILDERS', []))

def _find_objects_r(env, nodes, object_builders, objects, excludes, recur):
    """Helper function (recursion) for _find_objects()"""
    from SCons.Util import NodeList
    if recur <= 0:
        raise GCovRecursionError("Maximum recursion depth exceeded")
    children = NodeList()
    for node in nodes:
        if node not in excludes:
            children.extend(node.children())
            if node.has_builder():
                builder = node.get_builder()
                if builder in object_builders:
                    objects.append(node)
    if len(children) > 0:
        _find_objects_r(env, children, object_builders, objects, excludes, recur - 1)

def _find_objects(env, target):
    """Find all object files that the **target** node depends on.

    :Parameters:
        env: SCons.Environment.Environment
            a SCons Environment object
        target:
            node where we start our recursive search, usually program name or
            an alias which depends on one or more programs. Of course  it may
            be a list of such things. Typically it's an alias target which runs
            test program (the 'check' target).
    """
    from SCons.Util import NodeList, unique
    nodes = env.arg2nodes(target, target = target)
    object_builders = _get_object_builders(env)
    objects = NodeList()
    excludes = env.get('GCCCOV_EXCLUDE',[])
    excludes = env.arg2nodes(excludes, target = target)
    recur = env.get('GCCCOV_MAX_RECURSION', 256)
    _find_objects_r(env, nodes, object_builders, objects, excludes, recur)
    return NodeList(unique(objects))

def _object2gcda(env, objects, target):
    """Determine gcda files corresponding to a given objects"""
    import os
    from SCons.Util import NodeList, is_List
    objects = env.arg2nodes(objects, target = target)
    gcdas = NodeList()
    for obj in objects:
        gcda = os.path.splitext(str(obj))[0] + env.get('GCCCOV_GCDA_SUFFIX','.gcda')
        gcdas.append(gcda)
    excludes = env.get('GCCCOV_EXCLUDE',[])
    excludes = env.arg2nodes(excludes, target = target)
    gcdas = env.arg2nodes(gcdas, target = target)
    for exclude in excludes:
        if exclude in gcdas:
            gcdas.remove(exclude)
    return gcdas

def _detect_gcov(env):
    if env.has_key('GCCCOV'):
        return env['GCCCOV']
    return env.WhereIs('gcov')

def _FindGcdaNodes(env, root):
    """Find all *.gcda files that the **root** node should depend on.

    :Parameters:
        env: SCons.Environment.Environment
            a SCons Environment object
        root:
            node where we start our recursive search, usually program name or
            an alias which depends on one or more programs. Of course  it may
            be a list of such things. Typically it's an alias target which runs
            a test program (typically the 'check' target).
    """
    objects = _find_objects(env, root)
    return _object2gcda(env, objects, root)

def _InjectObjectEmitters(env, **overrides):
    """Inject object emitters

    :Parameters:
        env: SCons.Environment.Environment
            SCons environment object
        overrides : dict
            Used to override environment construction variables

    Injects our _GCovAwareObjectEmitter to all the obejct builders listed in
    ``GCCCOV_OBJECT_BUILDERS``.
    """
    from SCons.Util import is_Dict
    env = env.Override(overrides)
    if env.get('GCCCOV_DISABLE'):
        return
    builders = _get_object_builders(env)
    for builder in builders:
        if is_Dict(builder.emitter):
            emitters = builder.emitter
            suffixes = env.get('GCCCOV_SOURCE_SUFFIXES', emitters.keys())
            for sfx in suffixes:
                org_emitter = builder.emitter.get(sfx)
                if org_emitter and not isinstance(org_emitter, _GCovAwareObjectEmitter):
                    emitters[sfx] = _GCovAwareObjectEmitter(org_emitter)
        else:
            org_emitter = builder.emitter
            if not isinstance(org_emitter, _GCovAwareObjectEmitter):
                builder.emitter = _GCovAwareObjectEmitter(org_emitter)

def _InjectRuntestSideEffects(env, target, target_factory = _null, **overrides):
    from SCons.Util import NodeList
    env = env.Override(overrides)
    if env.get('GCCCOV_DISABLE'):
        return target
    if target_factory is _null:
        target_factory = env.get('GCCCOV_RUNTEST_FACTORY', env.ans.Alias)
    target = env.arg2nodes(target, target_factory, target = target)
    result = { }
    for tgt in target:
        gcda = _FindGcdaNodes(env, tgt)
        env.SideEffect(gcda, tgt)
        noclean = env.get('GCCCOV_NOCLEAN',[])
        noclean = env.arg2nodes(noclean, target = tgt)
        clean = NodeList([ f for f in gcda if f not in noclean ])
        noignore = env.get('GCCCOV_NOIGNORE',[])
        noignore = env.arg2nodes(noignore, target = tgt)
        ignore = NodeList([ f for f in gcda if f not in noignore])
        if len(clean) > 0:
            env.Clean(tgt, clean)
        if len(ignore) > 0:
            env.Ignore('.', gcda)
        result[tgt] = gcda
    return result

def generate(env):
    """Add gcov Builders and construction variables to the Environment"""
    import SCons.Util, SCons.Tool, SCons.Builder

    env.SetDefault( GCCCOV_OBJECT_BUILDERS = ['Object', 'StaticObject', 'SharedObject'],
                    GCCCOV_GCNO_SUFFIX = '.gcno',
                    GCCCOV_GCDA_SUFFIX = '.gcda',
                    GCCCOV_SUFFIX = '.gcov' )

    env.AddMethod(_InjectObjectEmitters, 'GCovInjectObjectEmitters')
    env.AddMethod(_FindGcdaNodes, 'GCovFindGcdaNodes')
    env.AddMethod(_InjectRuntestSideEffects, 'GCovInjectRuntestSideEffects')

def exists(env):
    return 1


# Local Variables:
# # tab-width:4
# # indent-tabs-mode:nil
# # End:
# vim: set syntax=scons expandtab tabstop=4 shiftwidth=4:
