from pathlib import Path

p = Path("fs/proc/fd.c")
s = p.read_text()

old = """\tseq_printf(m, "pos:\\t%lli\\nflags:\\t0%o\\nmnt_id:\\t%i\\nino:\\t%lu\\n",
\t\t   (long long)file->f_pos, f_flags,
\t\t   real_mount(file->f_path.mnt)->mnt_id,
\t\t   file_inode(file)->i_ino);

"""

new = """#ifdef CONFIG_KSU_SUSFS_SUS_KSTAT
\tif (susfs_is_current_app_uid()) {
\t\tstruct inode *inode = file_inode(file);
\t\tbool is_fuse = false;
\t\tif (susfs_is_inode_sus_kstat(inode, &is_fuse)) {
\t\t\tint mnt_id = real_mount(file->f_path.mnt)->mnt_id;
\t\t\tunsigned long ino = inode->i_ino;
\t\t\tsusfs_sus_kstat_spoof_proc_fd_seq_show(&mnt_id, &ino, inode->i_sb->s_dev);
\t\t\tseq_printf(m, "pos:\\t%lli\\nflags:\\t0%o\\nmnt_id:\\t%i\\nino:\\t%lu\\n",
\t\t\t\t\t(long long)file->f_pos, f_flags, mnt_id, ino);
\t\t\tgoto bypass_orig_flow;
\t\t}
\t}
#endif

#ifdef CONFIG_KSU_SUSFS_SUS_MOUNT
\tif (likely(susfs_is_current_proc_umounted())) {
\t\tstruct mount *mnt = real_mount(file->f_path.mnt);
\t\tif (mnt->mnt_id >= DEFAULT_KSU_MNT_ID) {
\t\t\tstruct path path;
\t\t\tchar *pathname = kmalloc(PAGE_SIZE, GFP_KERNEL);
\t\t\tchar *dpath;
\t\t\tif (!pathname)
\t\t\t\tgoto orig_flow;
\t\t\tdpath = d_path(&file->f_path, pathname, PAGE_SIZE);
\t\t\tif (!dpath)
\t\t\t\tgoto out_kfree;
\t\t\tif (kern_path(dpath, 0, &path))
\t\t\t\tgoto out_kfree;
\t\t\tif (!d_backing_inode(path.dentry))
\t\t\t\tgoto out_path_put;
\t\t\tseq_printf(m, "pos:\\t%lli\\nflags:\\t0%o\\nmnt_id:\\t%i\\nino:\\t%lu\\n",
\t\t\t\t\t(long long)file->f_pos, f_flags,
\t\t\t\t\tsusfs_get_non_sus_mnt_id_from_mnt(mnt),
\t\t\t\t\td_backing_inode(path.dentry)->i_ino);
\t\t\tpath_put(&path);
\t\t\tkfree(pathname);
\t\t\tgoto bypass_orig_flow;
out_path_put:
\t\t\tpath_put(&path);
out_kfree:
\t\t\tkfree(pathname);
\t\t\tgoto orig_flow;
\t\t}
\t}
orig_flow:
#endif

\t/* Preserve the exact stock Miami fdinfo format in the normal path. */
\tseq_printf(m, "pos:\\t%lli\\nflags:\\t0%o\\nmnt_id:\\t%i\\nino:\\t%lu\\n",
\t\t   (long long)file->f_pos, f_flags,
\t\t   real_mount(file->f_path.mnt)->mnt_id,
\t\t   file_inode(file)->i_ino);

#if defined(CONFIG_KSU_SUSFS_SUS_MOUNT) || defined(CONFIG_KSU_SUSFS_SUS_KSTAT)
bypass_orig_flow:
#endif
"""

if old not in s:
    raise SystemExit("Miami fd.c expected stock seq_show block not found")
p.write_text(s.replace(old, new, 1))
print("Applied Miami-specific SUSFS fs/proc/fd.c adaptation")
